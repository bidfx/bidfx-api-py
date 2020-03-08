import unittest

from bidfx.pricing._pixie.util.buffer_reads import scale_to_double


class TestScaleToDouble(unittest.TestCase):
    def test_scale_0(self):
        self.assertEqual("1234567890.0", scale_to_double(1234567890, 0))
        self.assertEqual("1234567890125.0", scale_to_double(1234567890125, 0))
        self.assertEqual("1234567890123456.0", scale_to_double(1234567890123456, 0))
        self.assertEqual("1234567890250000.0", scale_to_double(1234567890250000, 0))
        self.assertEqual("1234567890250002.0", scale_to_double(1234567890250002, 0))
        self.assertEqual("1234567890250020.0", scale_to_double(1234567890250020, 0))
        self.assertEqual("0.0", scale_to_double(0, 0))
        self.assertEqual("5.0", scale_to_double(5, 0))
        self.assertEqual("20.0", scale_to_double(20, 0))
        self.assertEqual("250.0", scale_to_double(250, 0))

    def test_scale_1(self):
        self.assertEqual("123456789.0", scale_to_double(1234567890, 1))
        self.assertEqual("123456789012.5", scale_to_double(1234567890125, 1))
        self.assertEqual("123456789012345.6", scale_to_double(1234567890123456, 1))
        self.assertEqual("123456789025000.0", scale_to_double(1234567890250000, 1))
        self.assertEqual("123456789025000.2", scale_to_double(1234567890250002, 1))
        self.assertEqual("123456789025002.0", scale_to_double(1234567890250020, 1))
        self.assertEqual("0.0", scale_to_double(0, 1))
        self.assertEqual("0.5", scale_to_double(5, 1))
        self.assertEqual("2.0", scale_to_double(20, 1))
        self.assertEqual("25.0", scale_to_double(250, 1))

    def test_scale_2(self):
        self.assertEqual("12345678.9", scale_to_double(1234567890, 2))
        self.assertEqual("12345678901.25", scale_to_double(1234567890125, 2))
        self.assertEqual("12345678901234.56", scale_to_double(1234567890123456, 2))
        self.assertEqual("12345678902500.0", scale_to_double(1234567890250000, 2))
        self.assertEqual("12345678902500.02", scale_to_double(1234567890250002, 2))
        self.assertEqual("12345678902500.2", scale_to_double(1234567890250020, 2))
        self.assertEqual("0.0", scale_to_double(0, 2))
        self.assertEqual("0.05", scale_to_double(5, 2))
        self.assertEqual("0.2", scale_to_double(20, 2))
        self.assertEqual("2.5", scale_to_double(250, 2))

    def test_scale_3(self):
        self.assertEqual("1234567.89", scale_to_double(1234567890, 3))
        self.assertEqual("1234567890.125", scale_to_double(1234567890125, 3))
        self.assertEqual("1234567890123.456", scale_to_double(1234567890123456, 3))
        self.assertEqual("1234567890250.0", scale_to_double(1234567890250000, 3))
        self.assertEqual("1234567890250.002", scale_to_double(1234567890250002, 3))
        self.assertEqual("1234567890250.02", scale_to_double(1234567890250020, 3))
        self.assertEqual("0.0", scale_to_double(0, 3))
        self.assertEqual("0.005", scale_to_double(5, 3))
        self.assertEqual("0.02", scale_to_double(20, 3))
        self.assertEqual("0.25", scale_to_double(250, 3))

    def test_scale_6(self):
        self.assertEqual("1234.56789", scale_to_double(1234567890, 6))
        self.assertEqual("1234567.890125", scale_to_double(1234567890125, 6))
        self.assertEqual("1234567890.123456", scale_to_double(1234567890123456, 6))
        self.assertEqual("1234567890.25", scale_to_double(1234567890250000, 6))
        self.assertEqual("1234567890.250002", scale_to_double(1234567890250002, 6))
        self.assertEqual("1234567890.25002", scale_to_double(1234567890250020, 6))
        self.assertEqual("0.0", scale_to_double(0, 6))
        self.assertEqual("0.000005", scale_to_double(5, 6))
        self.assertEqual("0.00002", scale_to_double(20, 6))
        self.assertEqual("0.00025", scale_to_double(250, 6))

    def test_scale_12(self):
        self.assertEqual("0.00123456789", scale_to_double(1234567890, 12))
        self.assertEqual("1.234567890125", scale_to_double(1234567890125, 12))
        self.assertEqual("1234.567890123456", scale_to_double(1234567890123456, 12))
        self.assertEqual("1234.56789025", scale_to_double(1234567890250000, 12))
        self.assertEqual("1234.567890250002", scale_to_double(1234567890250002, 12))
        self.assertEqual("1234.56789025002", scale_to_double(1234567890250020, 12))
        self.assertEqual("0.0", scale_to_double(0, 12))
        self.assertEqual("0.000000000005", scale_to_double(5, 12))
        self.assertEqual("0.00000000002", scale_to_double(20, 12))
        self.assertEqual("0.00000000025", scale_to_double(250, 12))

    def test_negative_scale_8(self):
        self.assertEqual("-64.391", scale_to_double(-6439100000, 8))
        self.assertEqual("-6.439", scale_to_double(-643900000, 8))
        self.assertEqual("-64.1", scale_to_double(-6410000000, 8))
        self.assertEqual("-64.99999999", scale_to_double(-6499999999, 8))
        self.assertEqual("-64.00000001", scale_to_double(-6400000001, 8))
        self.assertEqual("-1.45622", scale_to_double(-145622000, 8))

    def test_negative_scale_0(self):
        self.assertEqual("-1234567890.0", scale_to_double(-1234567890, 0))
        self.assertEqual("-1234567890125.0", scale_to_double(-1234567890125, 0))
        self.assertEqual("-1234567890123456.0", scale_to_double(-1234567890123456, 0))
        self.assertEqual("-1234567890250000.0", scale_to_double(-1234567890250000, 0))
        self.assertEqual("-1234567890250002.0", scale_to_double(-1234567890250002, 0))
        self.assertEqual("-1234567890250020.0", scale_to_double(-1234567890250020, 0))
        self.assertEqual("0.0", scale_to_double(-0, 0))
        self.assertEqual("-5.0", scale_to_double(-5, 0))
        self.assertEqual("-20.0", scale_to_double(-20, 0))
        self.assertEqual("-250.0", scale_to_double(-250, 0))

    def test_negative_scale_1(self):
        self.assertEqual("-123456789.0", scale_to_double(-1234567890, 1))
        self.assertEqual("-123456789012.5", scale_to_double(-1234567890125, 1))
        self.assertEqual("-123456789012345.6", scale_to_double(-1234567890123456, 1))
        self.assertEqual("-123456789025000.0", scale_to_double(-1234567890250000, 1))
        self.assertEqual("-123456789025000.2", scale_to_double(-1234567890250002, 1))
        self.assertEqual("-123456789025002.0", scale_to_double(-1234567890250020, 1))
        self.assertEqual("0.0", scale_to_double(-0, 1))
        self.assertEqual("-0.5", scale_to_double(-5, 1))
        self.assertEqual("-2.0", scale_to_double(-20, 1))
        self.assertEqual("-25.0", scale_to_double(-250, 1))

    def test_negative_scale_2(self):
        self.assertEqual("-12345678.9", scale_to_double(-1234567890, 2))
        self.assertEqual("-12345678901.25", scale_to_double(-1234567890125, 2))
        self.assertEqual("-12345678901234.56", scale_to_double(-1234567890123456, 2))
        self.assertEqual("-12345678902500.0", scale_to_double(-1234567890250000, 2))
        self.assertEqual("-12345678902500.02", scale_to_double(-1234567890250002, 2))
        self.assertEqual("-12345678902500.2", scale_to_double(-1234567890250020, 2))
        self.assertEqual("0.0", scale_to_double(-0, 2))
        self.assertEqual("-0.05", scale_to_double(-5, 2))
        self.assertEqual("-0.2", scale_to_double(-20, 2))
        self.assertEqual("-2.5", scale_to_double(-250, 2))

    def test_negative_scale_3(self):
        self.assertEqual("-1234567.89", scale_to_double(-1234567890, 3))
        self.assertEqual("-1234567890.125", scale_to_double(-1234567890125, 3))
        self.assertEqual("-1234567890123.456", scale_to_double(-1234567890123456, 3))
        self.assertEqual("-1234567890250.0", scale_to_double(-1234567890250000, 3))
        self.assertEqual("-1234567890250.002", scale_to_double(-1234567890250002, 3))
        self.assertEqual("-1234567890250.02", scale_to_double(-1234567890250020, 3))
        self.assertEqual("0.0", scale_to_double(-0, 3))
        self.assertEqual("-0.005", scale_to_double(-5, 3))
        self.assertEqual("-0.02", scale_to_double(-20, 3))
        self.assertEqual("-0.25", scale_to_double(-250, 3))

    def test_negative_scale_6(self):
        self.assertEqual("-1234.56789", scale_to_double(-1234567890, 6))
        self.assertEqual("-1234567.890125", scale_to_double(-1234567890125, 6))
        self.assertEqual("-1234567890.123456", scale_to_double(-1234567890123456, 6))
        self.assertEqual("-1234567890.25", scale_to_double(-1234567890250000, 6))
        self.assertEqual("-1234567890.250002", scale_to_double(-1234567890250002, 6))
        self.assertEqual("-1234567890.25002", scale_to_double(-1234567890250020, 6))
        self.assertEqual("0.0", scale_to_double(-0, 6))
        self.assertEqual("-0.000005", scale_to_double(-5, 6))
        self.assertEqual("-0.00002", scale_to_double(-20, 6))
        self.assertEqual("-0.00025", scale_to_double(-250, 6))

    def test_negative_scale_12(self):
        self.assertEqual("-0.00123456789", scale_to_double(-1234567890, 12))
        self.assertEqual("-1.234567890125", scale_to_double(-1234567890125, 12))
        self.assertEqual("-1234.567890123456", scale_to_double(-1234567890123456, 12))
        self.assertEqual("-1234.56789025", scale_to_double(-1234567890250000, 12))
        self.assertEqual("-1234.567890250002", scale_to_double(-1234567890250002, 12))
        self.assertEqual("-1234.56789025002", scale_to_double(-1234567890250020, 12))
        self.assertEqual("0.0", scale_to_double(-0, 12))
        self.assertEqual("-0.000000000005", scale_to_double(-5, 12))
        self.assertEqual("-0.00000000002", scale_to_double(-20, 12))
        self.assertEqual("-0.00000000025", scale_to_double(-250, 12))
