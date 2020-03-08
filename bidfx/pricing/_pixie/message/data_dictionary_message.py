from bidfx.pricing._pixie.message.field_def_message import FieldDefMessage
from .pixie_message_type import PixieMessageType
from ..util.varint import decode_varint


class DataDictionaryMessage:
    msg_type = PixieMessageType.DataDictionaryMessage

    def __init__(self, input_buff, decompressor):
        option = decode_varint(input_buff)
        self.is_updated = bool(option & 2)
        self.is_compressed = bool(option & 1)
        self.size = decode_varint(input_buff)
        if self.is_compressed:
            input_buff = decompressor.decompress(input_buff)  # decompressing using zlib
        self.definitions = [
            FieldDefMessage.create_from_bytes(input_buff) for _ in range(self.size)
        ]

    def get_data_dict(self):
        """
        Represent FieldDef message as dict instance.
        :return: dict of FieldID and Field Values
        """
        return {i.fid: i for i in self.definitions}

    def __str__(self):
        return (
            f"Data Dictionary message - compressed:{self.is_compressed} updated:{self.is_updated} "
            f"size:{self.size} definitions:{str(self.definitions)}"
        )
