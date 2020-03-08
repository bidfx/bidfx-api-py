import logging
import struct
from typing import Callable

from bidfx.exceptions import PricingError
from bidfx.pricing._pixie.util.buffer_reads import (
    read_double_fixed8,
    read_long_fixed8,
    read_int_fixed4,
    read_fixed1,
    read_fixed2,
    read_fixed3,
    read_fixed4,
    read_fixed8,
    read_fixed16,
    read_byte_array,
    read_byte,
    scale_to_double,
    scale_to_long,
)
from bidfx.pricing._pixie.util.varint import decode_string, decode_varint, decode_zigzag

log = logging.getLogger("bidfx.pricing.pixie.message")


class FieldType:
    FIELD_TYPES = {
        "D": read_double_fixed8,
        "L": read_long_fixed8,
        "I": read_int_fixed4,
        "S": decode_string,
    }

    @classmethod
    def by_code(cls, code):
        if code in cls.FIELD_TYPES:
            return cls.FIELD_TYPES[code]
        else:
            raise PricingError(f"unexpected Pixie price field type: {code}")


class FieldEncoding:
    FIELD_ENCODING = {
        "0": None,
        "1": read_fixed1,
        "2": read_fixed2,
        "3": read_fixed3,
        "4": read_fixed4,
        "8": read_fixed8,
        "@": read_fixed16,
        "B": read_byte_array,
        "V": decode_varint,
        "Z": decode_zigzag,
        "S": decode_string,
    }

    @classmethod
    def by_code(cls, code):
        if code in cls.FIELD_ENCODING:
            return cls.FIELD_ENCODING[code]
        else:
            raise PricingError(f"unexpected Pixie price field encoding: {code}")


LEGACY_FIELDS = ("Status", "SystemTime", "SystemLatency", "HopLatency1", "HopLatency2")


class FieldDefMessage:
    def __init__(
        self,
        fid: int,
        field_type: Callable,
        field_encoding: Callable,
        scale: int,
        name: str,
    ):
        self.fid = fid
        self.type = field_type
        self.encoding = field_encoding
        self.scale = scale
        self.name = name
        self.enabled = name not in LEGACY_FIELDS
        log.debug(str(self))

    @classmethod
    def create_from_bytes(cls, buffer):
        fid = decode_varint(buffer)
        field_type = FieldType.by_code(read_byte(buffer).decode("ascii"))
        field_encoding = FieldEncoding.by_code(read_byte(buffer).decode("ascii"))
        scale = decode_varint(buffer)
        name = decode_string(buffer)
        return cls(fid, field_type, field_encoding, scale, name)

    def parse_value(self, buffer) -> str:
        if self.type == read_double_fixed8:
            value = self._parse_double_value(buffer)
        elif self.type == read_long_fixed8 or self.type == read_int_fixed4:
            value = self._parse_int_value(buffer)
        else:  # STRING
            value = self.type(buffer)
        return value

    def __str__(self):
        return (
            f"Field Def Message FID:{self.fid} type:{self.type} encoding:{self.encoding} "
            f"scale:{self.scale} name:{self.name} enabled:{self.enabled}"
        )

    def _parse_double_value(self, buffer) -> str:
        if self.encoding == decode_zigzag:
            value = self.encoding(decode_varint(buffer))
            value = scale_to_double(value, self.scale)
        elif self.encoding == decode_varint:
            value = scale_to_double(self.encoding(buffer), self.scale)
        elif self.encoding is None:
            value = self.type(buffer)
        elif self.encoding == read_fixed8:
            value = str(struct.unpack(">d", self.encoding(buffer))[0])
        else:
            value = str(struct.unpack(">f", self.encoding(buffer))[0])
        return value

    def _parse_int_value(self, buffer) -> str:
        if self.encoding == decode_zigzag:
            value = str(self.encoding(decode_varint(buffer)))
        elif self.encoding == decode_varint:
            value = scale_to_long(self.encoding(buffer), self.scale)
        elif self.encoding is None:
            value = str(self.type(buffer))
        else:
            value = str(int.from_bytes(self.encoding(buffer), byteorder="big"))
        return value
