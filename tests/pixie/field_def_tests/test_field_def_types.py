import unittest

from bidfx.exceptions import PricingError
from bidfx.pricing._pixie.message.field_def_message import FieldType
from bidfx.pricing._pixie.util.buffer_reads import (
    read_double_fixed8,
    read_long_fixed8,
    read_int_fixed4,
)
from bidfx.pricing._pixie.util.varint import decode_string


class TestFieldDefTypes(unittest.TestCase):
    def test_field_def_types(self):
        self.assertEqual(FieldType.by_code("D"), read_double_fixed8)
        self.assertEqual(FieldType.by_code("L"), read_long_fixed8)
        self.assertEqual(FieldType.by_code("I"), read_int_fixed4)
        self.assertEqual(FieldType.by_code("S"), decode_string)

        with self.assertRaises(PricingError) as error:
            FieldType.by_code("X")
            self.assertEqual(error, "Incorrect field type X")
