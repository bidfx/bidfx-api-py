from .pixie_message_type import PixieMessageType
from ..util.buffer_reads import read_int_fixed4
from ..util.varint import decode_varint


class WelcomeMessage:
    msg_type = PixieMessageType.WelcomeMessage

    def __init__(self, input_buff):
        self.options = decode_varint(input_buff)
        self.version = decode_varint(input_buff)
        self.client_id = read_int_fixed4(input_buff)
        self.server_id = read_int_fixed4(input_buff)

    def __str__(self):
        return (
            f"WelcomeMessage options:{self.options} version:{self.version} "
            f"clientID:{self.client_id} serverID:{self.server_id}"
        )
