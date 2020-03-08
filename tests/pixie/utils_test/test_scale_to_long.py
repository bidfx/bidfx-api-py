import unittest

from bidfx.pricing._pixie.util.buffer_reads import scale_to_long


class TestScaleToLong(unittest.TestCase):
    def test_scale_to_long(self):
        self.assertEqual(scale_to_long(1, 1), "10")
        self.assertEqual(scale_to_long(1, 2), "100")
        self.assertEqual(scale_to_long(1, 3), "1000")
        self.assertEqual(scale_to_long(1, 4), "10000")
        self.assertEqual(scale_to_long(1, 5), "100000")
        self.assertEqual(scale_to_long(1, 6), "1000000")

        self.assertEqual(scale_to_long(56, 1), "560")
        self.assertEqual(scale_to_long(123, 2), "12300")
        self.assertEqual(scale_to_long(678, 3), "678000")
        self.assertEqual(scale_to_long(55, 4), "550000")
