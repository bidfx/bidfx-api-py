import unittest

from bidfx.pricing._pixie.util.buffer_reads import *


class TestBufferReads(unittest.TestCase):
    def test_read_int_fixed4(self):
        self.assertEqual(
            12345,
            read_int_fixed4(bytearray(int.to_bytes(12345, byteorder="big", length=4))),
        )

    def test_read_byte(self):
        self.assertEqual(b"1", read_byte(bytearray(b"1",)))

    def test_read_double_fixed8(self):
        self.assertEqual(
            12345.123, read_double_fixed8(bytearray(struct.pack(">d", 12345.123)))
        )

    def test_read_long_fixed8(self):
        self.assertEqual(
            123123123123123123,
            read_long_fixed8(
                bytearray(int.to_bytes(123123123123123123, byteorder="big", length=8))
            ),
        )

    def test_read_fixed1(self):
        self.assertEqual(
            bytearray(b"\x01"),
            read_fixed1(bytearray(b"\x01\x02\x99\x99\x99\x99\x99\x99")),
        )

    def test_read_fixed2(self):
        self.assertEqual(
            bytearray(b"\x01\x02"),
            read_fixed2(bytearray(b"\x01\x02\x99\x99\x99\x99\x99\x99")),
        )

    def test_read_fixed3(self):
        self.assertEqual(
            bytearray(b"\x01\x02\x03"),
            read_fixed3(bytearray(b"\x01\x02\x03\x99\x99\x99\x99\x99\x99")),
        )

    def test_read_fixed4(self):
        self.assertEqual(
            bytearray(b"\x01\x02\x03\x04"),
            read_fixed4(bytearray(b"\x01\x02\x03\x04\x99\x99\x99\x99\x99\x99")),
        )

    def test_read_fixed8(self):
        self.assertEqual(
            bytearray(b"\x01\x02\x03\x04\x01\x02\x03\x04"),
            read_fixed8(
                bytearray(b"\x01\x02\x03\x04\x01\x02\x03\x04\x99\x99\x99\x99\x99\x99")
            ),
        )

    def test_read_fixed16(self):
        self.assertEqual(
            bytearray(
                b"\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04"
            ),
            read_fixed16(
                bytearray(
                    b"\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04"
                )
            ),
        )

    def test_read_array(self):
        self.assertEqual(
            bytearray(b"1234"), read_byte_array(bytearray(b"\x0412345678"))
        )
