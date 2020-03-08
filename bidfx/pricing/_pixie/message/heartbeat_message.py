import logging

from .pixie_message_type import PixieMessageType
from ..util.varint import encode_varint

log = logging.getLogger("bidfx.pricing.pixie.message")


class HeartbeatMessage:
    msg_type = PixieMessageType.HeartbeatMessage

    def __init__(self):
        log.debug("send heartbeat")

    def to_bytes(self):
        return encode_varint(len(self.msg_type)) + self.msg_type

    def __str__(self):
        return "HeartbeatMessage"
