import socket


def encode_varint(n: int) -> bytearray:
    buffer = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            buffer += bytes((b | 0x80,))
        else:
            buffer += bytes((b,))
            break
    return buffer


def decode_varint(buffer: bytearray) -> int:
    result = 0
    for offset in range(0, 64, 7):
        b = _read_bytes(buffer, 1)[0]
        result |= (b & 0x7F) << offset
        if b < 128:
            break
    return result


def encode_string(s: str) -> bytearray:
    buffer = bytearray()
    if s is None:
        buffer += b"\x00"
    elif len(s):
        utf = s.encode("utf-8")
        buffer += encode_varint(len(utf) + 1)
        buffer += utf
    else:
        buffer += b"\x01"
    return buffer


def decode_string(buffer: bytearray) -> str:
    length = decode_varint(buffer)
    s = None
    if length:
        length -= 1
        if length:
            utf = _read_bytes(buffer, length)
            s = utf.decode("utf-8")
        else:
            s = ""
    return s


def _read_bytes(buffer, length):
    data = buffer[:length]
    del buffer[:length]
    return data


def encode_strings_list(string_list: list) -> bytearray:
    buffer = bytearray()
    buffer += encode_varint(len(string_list))
    for s in string_list:
        buffer += encode_string(s)
    return buffer


def decode_strings_list(list_bytes) -> list:
    length = decode_varint(list_bytes)
    string_list = []
    if length:
        for _ in range(length):
            ss = decode_string(list_bytes)
            string_list.append(ss)
        return string_list
    else:
        return None


def encode_zigzag(value):
    return (value << 1) ^ (value >> 63)


def decode_zigzag(value):
    return (value >> 1) ^ -(value & 1)


def decode_varint_from_socket(socket_connection):
    result = 0
    for offset in range(0, 64, 7):
        byte_ = read_bytes(socket_connection, 1)
        b = ord(byte_)
        result |= (b & 0x7F) << offset
        if b < 128:
            break
    return result


def read_bytes(socket_connection, length):
    result = b""

    while len(result) != length:
        byte_ = socket_connection.recv(length - len(result))
        if byte_ == b"":
            raise socket.error("end of socket stream")
        result += byte_
        
    return result
