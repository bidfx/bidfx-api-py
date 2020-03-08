from datetime import datetime

from .pixie_message_type import PixieMessageType
from ..util.varint import encode_varint


class AckMessage:
    msg_type = PixieMessageType.AckMessage

    def __init__(self, revision, revision_time, price_received_time):
        self.revision = revision
        self.revision_time = revision_time
        self.price_received_time = price_received_time
        self.ack_time = int(datetime.utcnow().timestamp() * 1000)
        self.handling_time = self.ack_time - self.price_received_time

    def to_bytes(self):
        ack_message = self.msg_type
        ack_message += encode_varint(self.revision)
        ack_message += encode_varint(self.revision_time)
        ack_message += encode_varint(self.price_received_time)
        ack_message += encode_varint(self.ack_time)
        ack_message += encode_varint(self.handling_time)
        ack_message_bytes = encode_varint(len(ack_message))
        ack_message_bytes += ack_message
        return ack_message_bytes

    def __str__(self):
        return f"AckMessage Revision:{self.revision} Revision time: {self.revision_time} Price Received time:{self.price_received_time} Ack time:{self.ack_time}"
