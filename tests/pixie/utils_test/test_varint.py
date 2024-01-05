import unittest
from unittest import mock

from bidfx.pricing._pixie.util.varint import *


class TestVarintNumbers(unittest.TestCase):
    def test_encode_one_byte_ints(self):
        self.assertEqual(bytearray.fromhex("00"), encode_varint(0))
        self.assertEqual(bytearray.fromhex("01"), encode_varint(1))
        self.assertEqual(bytearray.fromhex("02"), encode_varint(2))
        self.assertEqual(bytearray.fromhex("10"), encode_varint(16))
        self.assertEqual(bytearray.fromhex("7f"), encode_varint(127))

    def test_encode_two_byte_ints(self):
        self.assertEqual(bytearray.fromhex("8001"), encode_varint(128))
        self.assertEqual(bytearray.fromhex("8101"), encode_varint(129))
        self.assertEqual(bytearray.fromhex("8201"), encode_varint(130))

    def test_encode_three_byte_ints(self):
        self.assertEqual(bytearray.fromhex("e807"), encode_varint(1000))
        self.assertEqual(bytearray.fromhex("ffff03"), encode_varint(65535))
        self.assertEqual(bytearray.fromhex("feff03"), encode_varint(65534))
        self.assertEqual(bytearray.fromhex("fdff03"), encode_varint(65533))

    def test_encode_four_byte_ints(self):
        self.assertEqual(bytearray.fromhex("80808001"), encode_varint(2097152))
        self.assertEqual(bytearray.fromhex("C096B102"), encode_varint(5000000))


class TestTwoWayEncodeDecode(unittest.TestCase):
    def test_encode_decode_first_1000_ints(self):
        for n in range(1000):
            self.assertEqual(n, decode_varint(encode_varint(n)))

    def test_encode_decode_powers_of_10(self):
        self.assertEqual(1, decode_varint(encode_varint(1)))
        self.assertEqual(10, decode_varint(encode_varint(10)))
        self.assertEqual(100, decode_varint(encode_varint(100)))
        self.assertEqual(1000, decode_varint(encode_varint(1000)))
        self.assertEqual(10000, decode_varint(encode_varint(10000)))
        self.assertEqual(100000, decode_varint(encode_varint(100000)))
        self.assertEqual(1000000, decode_varint(encode_varint(1000000)))
        self.assertEqual(10000000, decode_varint(encode_varint(10000000)))


class TestStrings(unittest.TestCase):
    def test_encode_null_string(self):
        self.assertEqual(bytearray(b"\x00"), encode_string(None))

    def test_encode_blank_string(self):
        self.assertEqual(bytearray(b"\x01"), encode_string(""))

    def test_decode_null_string(self):
        self.assertEqual(None, decode_string(bytearray(b"\x00")))

    def test_decode_blank_string(self):
        self.assertEqual("", decode_string(bytearray(b"\x01")))

    def test_decode_string(self):
        self.assertEqual("x", decode_string(bytearray(b"\x02x")))
        self.assertEqual("test", decode_string(bytearray(b"\x05test")))
        self.assertEqual(
            "testing 1, 2, 3", decode_string(bytearray(b"\x10testing 1, 2, 3"))
        )

    def test_encode_string(self):
        self.assertEqual(bytearray(b"\x02x"), encode_string("x"))
        self.assertEqual(bytearray(b"\x05test"), encode_string("test"))
        self.assertEqual(
            bytearray(b"\x10testing 1, 2, 3"), encode_string("testing 1, 2, 3")
        )

    def test_encode_string_non_ascii(self):
        s = "test π"
        encoded = b"\x08test \xcf\x80"
        self.assertEqual(encoded, encode_string(s))
        self.assertEqual(s, decode_string(bytearray(encoded)))

    def test_decode_encode_string(self):
        self.assertEqual(decode_string(encode_string("test string")), "test string")
        self.assertEqual(
            decode_string(encode_string("test string123")), "test string123"
        )

    def test_string_array(self):
        self.assertEqual(encode_strings_list(["one", "two"]), b"\x02\x04one\x04two")

    def test_varint_decode_encode_string_array(self):
        self.assertListEqual(
            decode_strings_list(encode_strings_list(["one", "two"])), ["one", "two"]
        )
        self.assertListEqual(
            decode_strings_list(
                encode_strings_list(["on123e", "twoewer", "on123e", "twoewer"])
            ),
            ["on123e", "twoewer", "on123e", "twoewer"],
        )


class TestZigzagEncoding(unittest.TestCase):
    def test_encode_zigzag(self):
        self.assertEqual(0, encode_zigzag(0))
        self.assertEqual(1, encode_zigzag(-1))
        self.assertEqual(2, encode_zigzag(1))
        self.assertEqual(3, encode_zigzag(-2))
        self.assertEqual(4, encode_zigzag(2))
        self.assertEqual(5, encode_zigzag(-3))
        self.assertEqual(2000, encode_zigzag(1000))
        self.assertEqual(1999, encode_zigzag(-1000))
        self.assertEqual(200000000000, encode_zigzag(100000000000))
        self.assertEqual(199999999999, encode_zigzag(-100000000000))

    def test_decode_zigzag(self):
        self.assertEqual(0, decode_zigzag(0))
        self.assertEqual(-1, decode_zigzag(1))
        self.assertEqual(1, decode_zigzag(2))
        self.assertEqual(-2, decode_zigzag(3))
        self.assertEqual(2, decode_zigzag(4))
        self.assertEqual(-3, decode_zigzag(5))
        self.assertEqual(1000, decode_zigzag(2000))
        self.assertEqual(-1000, decode_zigzag(1999))
        self.assertEqual(100000000000, decode_zigzag(200000000000))
        self.assertEqual(-100000000000, decode_zigzag(199999999999))


class TestReadFromSocket(unittest.TestCase):
    def test_decode_encode_varint_number1(self):
        int_value = 123123123123
        mock_socket = self._mocked_socket_bytes(int_value)
        self.assertEqual(int_value, decode_varint_from_socket(mock_socket))

    def test_decode_encode_varint_number2(self):
        int_value = 66666666
        mock_socket = self._mocked_socket_bytes(int_value)
        self.assertEqual(int_value, decode_varint_from_socket(mock_socket))

    def _mocked_socket_bytes(self, int_value):
        mock_socket = mock.Mock()
        value = [
            int.to_bytes(i, byteorder="little", length=1) for i in encode_varint(int_value)
        ]
        mock_socket.recv = lambda x: value.pop(x - 1)
        return mock_socket

    def test_reads_from_socket_until_requested_length_fulfilled(self):
        mock_socket = mock.Mock()
        values = [b"res", b"ult"]
        values.reverse()
        mock_socket.recv = lambda _: values.pop()

        self.assertEqual(b"result", read_bytes(mock_socket, 6))

    def test_only_reads_from_socket_requested_length(self):
        mock_socket = mock.Mock()
        values = [b"res", b"ult", b"extra"]
        values.reverse()
        mock_socket.recv = lambda _: values.pop()

        self.assertEqual(b"result", read_bytes(mock_socket, 6))