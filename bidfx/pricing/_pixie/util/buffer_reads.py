import struct

from ..util.varint import decode_varint


def read_byte(buffer):
    return buffer.pop(0).to_bytes(1, byteorder="big")


def read_double_fixed8(buffer):
    return struct.unpack(">d", read_fixed8(buffer))[0]


def read_long_fixed8(buffer):
    return int.from_bytes(read_fixed8(buffer), "big")


def read_int_fixed4(buffer):
    return int.from_bytes(read_fixed4(buffer), "big")


def read_fixed1(buffer):
    return _read_bytes(buffer, 1)


def read_fixed2(buffer):
    return _read_bytes(buffer, 2)


def read_fixed3(buffer):
    return _read_bytes(buffer, 3)


def read_fixed4(buffer):
    return _read_bytes(buffer, 4)


def read_fixed8(buffer):
    return _read_bytes(buffer, 8)


def read_fixed16(buffer):
    return _read_bytes(buffer, 16)


def read_byte_array(buffer):
    return _read_bytes(buffer, decode_varint(buffer))


def _read_bytes(buffer, length):
    bytes_ = buffer[:length]
    del buffer[:length]
    return bytes_


def scale_to_double(value, scale):
    if scale == 0:
        return str(value) + ".0"
    if value < 0:
        return "-" + _scale_down(abs(value), scale)
    return _scale_down(value, scale)


def _scale_down(value, scale):
    pow10 = _POWERS_OF_TEN[scale]
    whole = str(value // pow10)
    frac = str(pow10 + value % pow10)[1:]
    return whole + "." + frac[0] + frac[1:].rstrip("0")


_POWERS_OF_TEN = [
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000,
    10000000,
    100000000,
    1000000000,
    10000000000,
    100000000000,
    1000000000000,
    10000000000000,
    100000000000000,
    1000000000000000,
    10000000000000000,
    100000000000000000,
    1000000000000000000,
]


def scale_to_long(value, scale):
    return str(value * _POWERS_OF_TEN[scale])
