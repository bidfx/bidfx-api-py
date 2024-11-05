__all__ = ["PixieProvider"]

import logging
import threading
import time
import getpass
from datetime import datetime

from bidfx._bidfx_api import BIDFX_API_INFO
from bidfx.exceptions import PricingError, IncompatibleVersionError
from bidfx.pricing.callbacks import Callbacks
from .message.ack_message import AckMessage
from .message.data_dictionary_message import DataDictionaryMessage
from .message.grant_message import GrantMessage
from .message.heartbeat_message import HeartbeatMessage
from .message.login_message import LoginMessage
from .message.pixie_message_type import PixieMessageType
from .message.price_sync_message import PriceSyncMessage
from .message.subscription_sync_message import SubscriptionSyncMessage
from .message.welcome_message import WelcomeMessage
from .subscription_register import SubscriptionRegister
from .util.compression import Decompressor
from .util.varint import decode_varint_from_socket, read_bytes
from .._service_connector import ServiceConnector
from ..events import (
    ProviderEvent,
    ProviderStatus,
    SubscriptionEvent,
    SubscriptionStatus,
)
from ..provider import PriceProvider
from ..subject import Subject

log = logging.getLogger("bidfx.pricing.pixie")

CURRENT_PROTOCOL_VERSION = 4


class PixieProvider(PriceProvider):
    _instance = 0

    def __init__(self, config_section, callbacks: Callbacks):
        PixieProvider._instance += 1
        self._provider_name = f"Pixie-{PixieProvider._instance}"
        self._host = config_section["host"]
        self._valid_cn = config_section.get("valid_cn")
        self._valid_root_cert = config_section.get("valid_root_cert")
        self._port = config_section.getint("port", 443)
        self._username = config_section["username"]
        self._password = config_section["password"]
        self._product_serial = config_section.get("product_serial", "")
        self._default_account = config_section.get("default_account")
        self._min_interval = config_section.getint("min_interval", 100)
        self._service = config_section.get("service", "highway")
        self._heartbeat_interval = config_section.getint("heartbeat_interval", 10)
        self._reconnect_interval = config_section.getint("reconnect_interval", 10)
        self._tunnel = config_section.getboolean("tunnel", True)
        self._callbacks = callbacks
        self._subscription_register = SubscriptionRegister()
        self._data_dictionary = None
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
        level = subject[Subject.LEVEL]
        if level == "1":
            self._subscription_register.subscribe(subject)
        else:
            raise PricingError(
                f"the Pixie protocol does not yet support level={level} subscriptions"
            )

    def unsubscribe(self, subject):
        log.info(f"unsubscribe from: {subject}")
        self._subscription_register.unsubscribe(subject)

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
        self._decompressor = Decompressor()
        self._send_message(SubscriptionSyncMessage(1, []))

    def _open_connection(self):
        read_timeout = self._heartbeat_interval * 2
        connector = ServiceConnector(
            self._host, self._port, self._username, self._password, BIDFX_API_INFO.guid, self._valid_cn, self._valid_root_cert
        )
        if self._tunnel:
            return connector.tunnel_socket_to_service(self._service, read_timeout)
        return connector.direct_socket_to_service(read_timeout)

    def _send_protocol_signature(self):
        protocol_signature = (
            b"pixie://localhost?version=%d&heartbeat=%d&idle=120&minti=%d\n"
            % (CURRENT_PROTOCOL_VERSION, self._heartbeat_interval, self._min_interval)
        )
        self._opened_socket.sendall(protocol_signature)

    def _login_into_server(self):
        self._read_welcome_message()
        self._send_login_message()
        self._read_grant_message()
        self._read_data_dict_message()

    def _price_server_read_loop(self):
        try:
            while self._running:
                msg_type, buffer = self._read_message_bytes()
                self._handle_received_message(msg_type, buffer)
                del buffer
        except Exception as e:
            self._publish_provider_status(
                ProviderStatus.DOWN, f"connection error due to: {e}"
            )
            self._notify_all_subjects_as_stale(
                f"price provider {self._provider_name} is down"
            )

    def _handle_received_message(self, msg_type, buffer):
        if msg_type == PixieMessageType.PriceSyncMessage:
            price_received_time = int(datetime.utcnow().timestamp() * 1000)
            price_sync = PriceSyncMessage(buffer, self._decompressor)
            self._on_price_sync(price_sync)
            self._send_message(
                AckMessage(
                    price_sync.revision, price_sync.revision_time, price_received_time
                )
            )
            self._after_price_sync(price_sync.edition)

        elif msg_type == PixieMessageType.DataDictionaryMessage:
            self._handle_data_dictionary_message(buffer)

        elif msg_type == PixieMessageType.HeartbeatMessage:
            log.debug("receive heartbeat")

    def _on_price_sync(self, price_sync):
        subjects = self._subscription_register.subjects_for_edition(price_sync.edition)
        price_sync.visit_updates(subjects, self._data_dictionary, self._callbacks)

    def _after_price_sync(self, edition):
        self._subscription_register.purge_editions_before(edition)
        subscription_sync = self._subscription_register.subscription_sync()
        if subscription_sync:
            self._send_message(subscription_sync)
        else:
            self._check_heartbeats()

    def _read_message_bytes(self):
        length = decode_varint_from_socket(self._opened_socket)
        message_type = read_bytes(self._opened_socket, 1)
        return message_type, bytearray(read_bytes(self._opened_socket, length - 1))

    def _read_welcome_message(self):
        msg_type, buffer = self._read_message_bytes()
        if msg_type != PixieMessageType.WelcomeMessage:
            raise PricingError(
                f"{self._provider_name} expected a Welcome message but got {msg_type}"
            )
        welcome_msg = WelcomeMessage(buffer)
        log.debug(f"received message: {welcome_msg}")
        self._verify_version(welcome_msg.version)

    @staticmethod
    def _verify_version(server_version):
        if server_version != CURRENT_PROTOCOL_VERSION:
            msg = (
                f"a server negotiating Pixie protocol version {server_version} is "
                f"incompatible with this API client on version {CURRENT_PROTOCOL_VERSION}"
            )
            log.error(msg)
            raise IncompatibleVersionError(msg)
        else:
            log.info(f"client and server have agreed on Pixie version {server_version}")

    def _send_login_message(self):
        login_message = LoginMessage(
            self._username,
            self._password,
            getpass.getuser(),
            BIDFX_API_INFO.name,
            BIDFX_API_INFO.version,
            self._product_serial,
        )
        self._send_message(login_message)

    def _read_grant_message(self):
        msg_type, buffer = self._read_message_bytes()
        if msg_type != PixieMessageType.GrantMessage:
            raise PricingError(
                f"{self._provider_name} expected a Grant message but got {msg_type}"
            )
        grant_msg = GrantMessage(buffer)
        log.debug(f"received message: {grant_msg}")
        if grant_msg.granted == b"f":
            raise PricingError(
                f"login to {self._provider_name} rejected due to {grant_msg.reason}"
            )

    def _read_data_dict_message(self):
        msg_type, buffer = self._read_message_bytes()
        if msg_type != PixieMessageType.DataDictionaryMessage:
            raise PricingError(
                f"{self._provider_name} expected a Data Dictionary message but got {msg_type}"
            )
        self._handle_data_dictionary_message(buffer)

    def _handle_data_dictionary_message(self, buff):
        data_dict_msg = DataDictionaryMessage(buff, self._decompressor)
        log.debug(f"received message: {data_dict_msg}")
        if data_dict_msg.is_updated:
            self._data_dictionary.update(data_dict_msg.get_data_dict())
        else:
            self._data_dictionary = data_dict_msg.get_data_dict()
        log.debug("data dict instance: " + str(self._data_dictionary))

    def _send_message(self, message):
        log.debug("sending: " + str(message))
        self._opened_socket.sendall(message.to_bytes())
        self._last_time_write = time.time()

    def _check_heartbeats(self):
        if time.time() - self._last_time_write > self._heartbeat_interval:
            self._send_message(HeartbeatMessage())

    def _publish_provider_status(self, status: ProviderStatus, reason=""):
        event = ProviderEvent(self._provider_name, status, reason)
        log.info(str(event))
        self._callbacks.provider_event_fn(event)

    def _notify_all_subjects_as_stale(self, explanation):
        log.debug("notify all subjects as stale")
        subjects = self._subscription_register.reset_and_get_subjects()
        for subject in subjects:
            self._publish_subscription_status(
                subject, SubscriptionStatus.STALE, explanation
            )

    def _publish_subscription_status(self, subject, status, explanation):
        event = SubscriptionEvent(subject, status, explanation)
        log.info(str(event))
        self._callbacks.subscription_event_fn(event)
