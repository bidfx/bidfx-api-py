import logging

from .pixie_message_type import PixieMessageType
from ..util.buffer_reads import read_byte
from ..util.varint import decode_string

log = logging.getLogger("bidfx.pricing.pixie.message")


class GrantMessage:
    msg_type = PixieMessageType.GrantMessage

    def __init__(self, input_buff):
        log.debug("Grant message")
        self.granted = read_byte(input_buff)
        self.reason = decode_string(input_buff)

    def __str__(self):
        return f"GrantMessage Granted:{self.granted.decode()} Reason:{self.reason}"
