__all__ = ["PuffinProvider"]

import getpass
import logging
import threading
import time
from base64 import b64decode, b64encode

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA

from bidfx._bidfx_api import BIDFX_API_INFO
from bidfx.exceptions import PricingError, IncompatibleVersionError
from .element import Element, ElementParser
from .message_compressor import MessageCompressor
from .message_decompressor import MessageDecompressor
from .._service_connector import ServiceConnector
from ..callbacks import Callbacks
from ..events import (
    ProviderEvent,
    ProviderStatus,
    SubscriptionEvent,
    SubscriptionStatus,
    PriceEvent,
)
from ..provider import PriceProvider

log = logging.getLogger("bidfx.pricing.puffin")

CURRENT_PROTOCOL_VERSION = 8

_status_adaptor = [
    SubscriptionStatus.OK,
    SubscriptionStatus.PENDING,
    SubscriptionStatus.TIMEOUT,
    SubscriptionStatus.STALE,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.UNAVAILABLE,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.UNAVAILABLE,
    SubscriptionStatus.PROHIBITED,
    SubscriptionStatus.STALE,
    SubscriptionStatus.UNAVAILABLE,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.CLOSED,
    SubscriptionStatus.REJECTED,
    SubscriptionStatus.EXHAUSTED,
]


class SubscriptionSet:
    def __init__(self):
        self._lock = threading.Lock()
        self._subscribed_subjects = {}

    def subscribe(self, subject):
        with self._lock:
            self._subscribed_subjects[str(subject)] = subject

    def unsubscribe(self, subject):
        with self._lock:
            del self._subscribed_subjects[str(subject)]

    def subject_from_string(self, subject_str):
        with self._lock:
            return self._subscribed_subjects.get(subject_str, None)

    def active_subjects(self):
        with self._lock:
            return list(self._subscribed_subjects.values())


class PuffinProvider(PriceProvider):
    _instance = 0

    def __init__(self, config_section, callbacks: Callbacks):
        PuffinProvider._instance += 1
        self._provider_name = f"Puffin-{PuffinProvider._instance}"
        self._host = config_section["host"]
        self._valid_cn = config_section.get("valid_cn")
        self._valid_root_cert = config_section.get("valid_root_cert")
        self._port = config_section.getint("port", 443)
        self._username = config_section["username"]
        self._password = config_section["password"]
        self._service = config_section.get("service", "puffin")
        self._heartbeat_interval = config_section.getint("heartbeat_interval", 10)
        self._reconnect_interval = config_section.getint("reconnect_interval", 10)
        self._tunnel = config_section.getboolean("tunnel", True)
        self._callbacks = callbacks
        self._subscription_set = SubscriptionSet()
        self._compressor = None
        self._decompressor = None
        self._opened_socket = None
        self._last_time_write = 0
        self._running = False

    def start(self):
        if self._running:
            log.warning(f"attempt to start {self._provider_name} provider ignored")
        else:
            log.info(f"starting {self._provider_name} provider")
            self._publish_provider_status(ProviderStatus.DOWN, "starting up")
            self._running = True
            threading.Thread(
                target=self._init_connection,
                name=self._provider_name + "-read",
                daemon=True,
            ).start()

    def subscribe(self, subject):
        log.info(f"subscribe to: {subject}")
        self._subscription_set.subscribe(subject)
        self._send_subscribe(subject)

    def unsubscribe(self, subject):
        log.info(f"unsubscribe from: {subject}")
        self._subscription_set.unsubscribe(subject)
        self._send_unsubscribe(subject)

    def stop(self):
        log.info(f"stopping {self._provider_name} provider")
        self._running = False
        if self._opened_socket:
            self._opened_socket.close()

    def _init_connection(self):
        self._session_connection_attempt()
        while self._running:
            time.sleep(self._reconnect_interval)
            self._session_connection_attempt()

    def _session_connection_attempt(self):
        try:
            self._opened_socket = self._open_connection()
            self._send_protocol_signature()
            self._login_into_server()
            self._prepare_new_session()
            self._publish_provider_status(ProviderStatus.READY)
            self._price_server_read_loop()
        except Exception as e:
            log.warning(f"connection attempt failed due to: {e}")

    def _prepare_new_session(self):
        self._compressor = MessageCompressor(self._opened_socket)
        self._decompressor = MessageDecompressor(self._opened_socket)
        self._refresh_subscriptions()

    def _open_connection(self):
        connector = ServiceConnector(
            self._host, self._port, self._username, self._password, BIDFX_API_INFO.guid, self._valid_cn, self._valid_root_cert
        )
        read_timeout = self._heartbeat_interval * 2
        if self._tunnel:
            return connector.tunnel_socket_to_service(self._service, read_timeout)
        return connector.direct_socket_to_service(read_timeout)

    def _send_protocol_signature(self):
        protocol_signature = b"puffin://localhost?encrypt=false\n"
        self._opened_socket.sendall(protocol_signature)

    def _login_into_server(self):
        parser = ElementParser(self._opened_socket)
        welcome_msg = self._read_welcome_message(parser)
        self._heartbeat_interval = int(welcome_msg["Interval"]) / 1000
        log.debug(f"heartbeat interval changed to {self._heartbeat_interval} seconds")
        self._opened_socket.settimeout(self._heartbeat_interval * 2)
        self._send_login_message(welcome_msg["PublicKey"])
        self._read_grant_message(parser)

    def _price_server_read_loop(self):
        try:
            while self._running:
                message = self._decompressor.decompress_message()
                self._handle_received_message(message)
        except Exception as e:
            self._publish_provider_status(
                ProviderStatus.DOWN, f"connection error due to: {e}"
            )
            self._notify_all_subjects_as_stale(
                f"price provider {self._provider_name} is down"
            )

    def _handle_received_message(self, message: Element):
        msg_type = message.tag
        if msg_type == "Update":
            self._handle_price_update_message(message, full=False)
        elif msg_type == "Set":
            self._handle_price_update_message(message, full=True)
        elif msg_type == "Status":
            self._handle_price_status_message(message)
        elif msg_type == "Heartbeat":
            self._handle_heartbeat_message()

    def _handle_price_update_message(self, message: Element, full: bool):
        subject = self._subscribed_subject_attribute(message)
        if subject:
            price = message.extract_price()
            self._callbacks.price_event_fn(PriceEvent(subject, price, full))

    def _handle_price_status_message(self, message: Element):
        subject = self._subscribed_subject_attribute(message)
        if subject:
            status_id = int(message["Id"])
            status = self._puffin_status_adaptor(status_id)
            explanation = message.get("Text", "")
            self._publish_subscription_status(subject, status, explanation)

    @staticmethod
    def _puffin_status_adaptor(status_id: int):
        if status_id >= len(_status_adaptor):
            return SubscriptionStatus.UNAVAILABLE
        return _status_adaptor[status_id]

    def _handle_heartbeat_message(self):
        self._send_message(Element("Heartbeat"))

    def _subscribed_subject_attribute(self, element: Element):
        subject_str = element["Subject"]
        return self._subscription_set.subject_from_string(subject_str)

    def _read_welcome_message(self, parser) -> Element:
        welcome_msg = parser.parse_element()
        log.debug(f"Puffin sent message: {welcome_msg}")
        self._verify_version(int(welcome_msg["Version"]))
        return welcome_msg

    def _send_login_message(self, public_key):
        description = BIDFX_API_INFO.name + " " + BIDFX_API_INFO.version
        password = self._password
        if public_key:
            password = self._encrypted_password(public_key, password).decode("ascii")
        login_message = (
            Element("Login")
            .set("Name", self._username)
            .set("Password", password)
            .set("Version", str(8))
            .set("Description", description)
            .set("Alias", None or getpass.getuser())
        )
        self._send_message(login_message, compress=False)

    @staticmethod
    def _encrypted_password(public_key, password):
        try:
            raw_key = b64decode(public_key)
            key = RSA.importKey(raw_key)
            cipher = PKCS1_v1_5.new(key)
            return b64encode(cipher.encrypt(password.encode("utf-8")))
        except Exception as e:
            log.error(e)

    @staticmethod
    def _verify_version(server_version):
        if server_version != CURRENT_PROTOCOL_VERSION:
            msg = (
                f"a server negotiating Puffin protocol version {server_version} is "
                f"incompatible with this API client on version {CURRENT_PROTOCOL_VERSION}"
            )
            log.error(msg)
            raise IncompatibleVersionError(msg)
        else:
            log.info(
                f"client and server have agreed on Puffin version {server_version}"
            )

    def _read_grant_message(self, parser):
        grant_msg = parser.parse_element()
        log.debug(f"Puffin sent message: {grant_msg}")
        # skip the service description message
        service_description_msg = parser.parse_element()
        log.debug(f"Puffin sent message: {service_description_msg}")

        if grant_msg["Access"] == "true":
            message = (
                Element("ServiceDescription")
                .set("username", self._username)
                .set("alias", getpass.getuser())
                .set("server", "false")
                .set("discoverable", "false")
            )
            self._send_message(message, compress=False)
        else:
            raise PricingError(
                f"login to {self._provider_name} rejected due to {grant_msg.text}"
            )

    def _send_message(self, message: Element, compress=True):
        log.debug(f"sending: {message}")
        if compress:
            self._compressor.compress_message(message)
        else:
            self._opened_socket.sendall(str(message).encode("ascii"))
        self._last_time_write = time.time()

    def _publish_provider_status(self, status: ProviderStatus, reason=""):
        event = ProviderEvent(self._provider_name, status, reason)
        log.info(str(event))
        self._callbacks.provider_event_fn(event)

    def _notify_all_subjects_as_stale(self, explanation):
        log.debug("notify all subjects as stale")
        for subject in self._subscription_set.active_subjects():
            self._publish_subscription_status(
                subject, SubscriptionStatus.STALE, explanation
            )

    def _publish_subscription_status(self, subject, status, explanation):
        event = SubscriptionEvent(subject, status, explanation)
        log.info(str(event))
        self._callbacks.subscription_event_fn(event)

    def _refresh_subscriptions(self):
        for subject in self._subscription_set.active_subjects():
            self._send_subscribe(subject)

    def _send_subscribe(self, subject):
        if self._opened_socket:
            self._send_message(Element("Subscribe").set("Subject", str(subject)))

    def _send_unsubscribe(self, subject):
        if self._opened_socket:
            self._send_message(Element("Unsubscribe").set("Subject", str(subject)))
