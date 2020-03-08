import unittest

from bidfx.exceptions import PricingError
from bidfx.pricing._pixie.message.field_def_message import FieldEncoding
from bidfx.pricing._pixie.util.buffer_reads import (
    read_fixed1,
    read_fixed2,
    read_fixed3,
    read_fixed4,
    read_fixed8,
    read_fixed16,
    read_byte_array,
)
from bidfx.pricing._pixie.util.varint import decode_varint, decode_string, decode_zigzag


class TestFieldDefEncoding(unittest.TestCase):
    def test_field_def_encoding(self):
        self.assertEqual(FieldEncoding.by_code("0"), None)
        self.assertEqual(FieldEncoding.by_code("1"), read_fixed1)
        self.assertEqual(FieldEncoding.by_code("2"), read_fixed2)
        self.assertEqual(FieldEncoding.by_code("3"), read_fixed3)
        self.assertEqual(FieldEncoding.by_code("4"), read_fixed4)
        self.assertEqual(FieldEncoding.by_code("8"), read_fixed8)
        self.assertEqual(FieldEncoding.by_code("@"), read_fixed16)
        self.assertEqual(FieldEncoding.by_code("B"), read_byte_array)
        self.assertEqual(FieldEncoding.by_code("V"), decode_varint)
        self.assertEqual(FieldEncoding.by_code("Z"), decode_zigzag)
        self.assertEqual(FieldEncoding.by_code("S"), decode_string)

        with self.assertRaises(PricingError) as error:
            FieldEncoding.by_code("X")
            self.assertEqual(error, "Incorrect field encoding X")
