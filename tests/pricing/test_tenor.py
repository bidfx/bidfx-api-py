import unittest

from bidfx.exceptions import PricingError
from bidfx.pricing.tenor import Tenor


class TestTenor(unittest.TestCase):
    def test_tenor_strings(self):
        self.assertEqual("3W", Tenor.IN_3_WEEKS)
        self.assertEqual("3M", Tenor.IN_3_MONTHS)
        self.assertEqual("3Y", Tenor.IN_3_YEARS)
        self.assertEqual("BD", Tenor.BROKEN_DATE)
        self.assertEqual("TOD", Tenor.TODAY)
        self.assertEqual("TOM", Tenor.TOMORROW)
        self.assertEqual("Spot", Tenor.SPOT)
        self.assertEqual("S/N", Tenor.SPOT_NEXT)
        self.assertEqual("IMMU", Tenor.IMM_SEPTEMBER)

    def test_tenor_of_week(self):
        self.assertEqual(Tenor.IN_1_WEEK, Tenor.of_week(1))
        self.assertEqual(Tenor.IN_2_WEEKS, Tenor.of_week(2))
        self.assertEqual(Tenor.IN_3_WEEKS, Tenor.of_week(3))

    def test_tenor_of_week_fails_at_4(self):
        with self.assertRaises(PricingError) as error:
            Tenor.of_week(4)
        self.assertEqual("invalid weekly tenor of 4 weeks", str(error.exception))

    def test_tenor_of_month(self):
        self.assertEqual(Tenor.IN_1_MONTH, Tenor.of_month(1))
        self.assertEqual(Tenor.IN_2_MONTHS, Tenor.of_month(2))
        self.assertEqual(Tenor.IN_3_MONTHS, Tenor.of_month(3))
        self.assertEqual(Tenor.IN_9_MONTHS, Tenor.of_month(9))
        self.assertEqual(Tenor.IN_18_MONTHS, Tenor.of_month(18))
        self.assertEqual(Tenor.IN_30_MONTHS, Tenor.of_month(30))

    def test_tenor_of_month_fails_at_12(self):
        with self.assertRaises(PricingError) as error:
            Tenor.of_month(12)
        self.assertEqual("invalid monthly tenor of 12 months", str(error.exception))

    def test_tenor_of_month_fails_at_19(self):
        with self.assertRaises(PricingError) as error:
            Tenor.of_month(19)
        self.assertEqual("invalid monthly tenor of 19 months", str(error.exception))

    def test_tenor_of_year(self):
        self.assertEqual(Tenor.IN_1_YEAR, Tenor.of_year(1))
        self.assertEqual(Tenor.IN_2_YEARS, Tenor.of_year(2))
        self.assertEqual(Tenor.IN_3_YEARS, Tenor.of_year(3))
        self.assertEqual(Tenor.IN_4_YEARS, Tenor.of_year(4))
        self.assertEqual(Tenor.IN_5_YEARS, Tenor.of_year(5))

    def test_tenor_of_year_fails_at_6(self):
        with self.assertRaises(PricingError) as error:
            Tenor.of_year(6)
        self.assertEqual("invalid yearly tenor of 6 years", str(error.exception))

    def test_tenor_of_imm_month(self):
        self.assertEqual(Tenor.IMM_MARCH, Tenor.of_imm_month(3))
        self.assertEqual(Tenor.IMM_JUNE, Tenor.of_imm_month(6))
        self.assertEqual(Tenor.IMM_SEPTEMBER, Tenor.of_imm_month(9))
        self.assertEqual(Tenor.IMM_DECEMBER, Tenor.of_imm_month(12))

    def test_tenor_of_imm_month_fails_for_january(self):
        with self.assertRaises(PricingError) as error:
            Tenor.of_imm_month(1)
        self.assertEqual("invalid IMM monthly tenor for month 1", str(error.exception))
        with self.assertRaises(PricingError) as error:
            Tenor.of_imm_month(2)
        self.assertEqual("invalid IMM monthly tenor for month 2", str(error.exception))
        with self.assertRaises(PricingError) as error:
            Tenor.of_imm_month(11)
        self.assertEqual("invalid IMM monthly tenor for month 11", str(error.exception))
