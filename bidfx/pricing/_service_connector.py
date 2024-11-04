__all__ = ["ServiceConnector"]

import logging
import socket
import ssl
from base64 import b64encode
from datetime import datetime

log = logging.getLogger("bidfx.pricing.tunnel")

CIPHER_SUITES = (
    "ECDHE-ECDSA-AES256-GCM-SHA384:"
    "ECDHE-ECDSA-AES256-SHA:"
    "ECDHE-ECDSA-AES256-SHA384:"
    "ECDHE-RSA-AES256-GCM-SHA384:"
    "ECDHE-RSA-AES256-SHA:"
    "ECDHE-RSA-AES256-SHA384:"
    "DHE-RSA-AES256-GCM-SHA384:"
    "DHE-RSA-AES256-SHA:"
    "DHE-RSA-AES256-SHA256:"
    "DHE-RSA-AES256-SHA256:"
    "EDH-RSA-DES-CBC3-SHA"
)


class ServiceConnector:
    def __init__(self, host, port, username, password, guid, valid_cn, valid_root_cert):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._guid = guid
        self._valid_cn = valid_cn
        self._valid_root_cert = valid_root_cert

    def tunnel_socket_to_service(self, service, read_timeout):
        opened_socket = self._open_secure_socket(read_timeout)
        self._tunnel_to_service(opened_socket, service)
        return opened_socket

    def direct_socket_to_service(self, read_timeout):
        log.info(f"opening a connection to {self._username}@{self._host}:{self._port}")
        opened_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        opened_socket.settimeout(read_timeout)
        try:
            opened_socket.connect((self._host, self._port))
        except Exception as ex:
            raise ConnectionRefusedError(
                f"could not open socket to {self._host}:{self._port} due to {ex}"
            )
        return opened_socket

    def _open_secure_socket(self, read_timeout):
        log.info(
            f"opening a secure connection to {self._username}@{self._host}:{self._port}"
        )
        opened_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        opened_socket.settimeout(read_timeout)
        opened_socket = self._wrap_as_secure_socket(opened_socket)
        try:
            opened_socket.connect((self._host, self._port))
        except Exception as ex:
            raise ConnectionRefusedError(
                f"could not open socket to {self._host}:{self._port} due to {ex}"
            )
        self._validate_certificate(opened_socket)
        return opened_socket

    def _validate_certificate(self, opened_socket):
        cert = opened_socket.getpeercert()
        before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
        after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        if not before < datetime.utcnow() < after:
            raise ssl.CertificateError("certificate expired")

    def _wrap_as_secure_socket(self, opened_socket):
        host_name = self._valid_cn if self._valid_cn else self._host
        log.info(f"Wrapping SSL socket with server_hostname {host_name}")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.set_ciphers(CIPHER_SUITES)
        ssl_context.check_hostname = True
        if self._valid_root_cert:
            log.info(f"Loading root certificate {self._valid_root_cert}")
            ssl_context.load_verify_locations(cafile=self._valid_root_cert)
        else:
            ssl_context.load_default_certs()
        opened_socket = ssl_context.wrap_socket(
            opened_socket, server_hostname=host_name
        )
        return opened_socket

    def _tunnel_to_service(self, opened_socket, service):
        log.info(f"tunnelling to {service} service")
        login_and_path_in_base64 = b64encode(
            f"{self._username}:{self._password}".encode("utf-8")
        ).decode()
        header = (
            f"CONNECT static://{service} HTTP/1.1\r\n"
            f"Authorization: Basic {login_and_path_in_base64}\r\nGUID: {self._guid}\r\n\r\n"
        )
        opened_socket.sendall(header.encode("utf-8"))
        received_response = opened_socket.recv(4096)
        log.debug("received: " + repr(received_response))
        if b"200 OK" not in received_response:
            log.warning("tunnel return error status: " + repr(received_response))
            raise ConnectionAbortedError("tunnel return non 200 status")
