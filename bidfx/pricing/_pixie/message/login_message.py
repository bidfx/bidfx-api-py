import logging

from .pixie_message_type import PixieMessageType
from ..util.varint import encode_string, encode_varint

log = logging.getLogger("bidfx.pricing.pixie.message")


class LoginMessage:
    msg_type = PixieMessageType.LoginMessage

    def __init__(self, username, password, alias, api, api_version, product_serial):
        self._username = username
        self._password = password
        self._alias = alias
        self._api = api
        self._api_version = api_version
        self._product_serial = product_serial

    def to_bytes(self):
        login_message = self.msg_type
        login_message += encode_string(self._username)
        login_message += encode_string(self._password)
        login_message += encode_string(self._alias)
        login_message += encode_string(self._api)
        login_message += encode_string(self._api_version)
        # Deliberately use the API for the application info in the Public version of the API.
        login_message += encode_string(self._api)
        login_message += encode_string(self._api_version)
        login_message += encode_string("BidFXPython")
        login_message += encode_string(self._product_serial)
        login_message_bytes = encode_varint(len(login_message))
        login_message_bytes += login_message
        log.debug("login message: " + str(login_message_bytes.hex()))
        return login_message_bytes

    def __str__(self):
        return f"LoginMessage Login:{self._username} Alias:{self._alias} ProductSerial:{self._product_serial}"
