from unittest import TestCase

from bidfx import Subject


class TestLengthCountsNumberOfComponentPairs(TestCase):
    def test_length_of_4_part_subject_is_4(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "GBP"),
                ("Quantity", "1000.00"),
                ("Symbol", "GBPUSD"),
            )
        )
        self.assertEqual(len(subject), 4)

    def test_length_of_1_part_subject_is_1(self):
        subject = Subject((("Symbol", "GBPUSD"),))
        self.assertEqual(len(subject), 1)

    def test_length_of_empty_subject_is_0(self):
        subject = Subject((),)
        self.assertEqual(len(subject), 0)


class TestSubjectToString(TestCase):
    def test_EURUSD_subject_to_string(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "EUR"),
                ("Quantity", "10000.00"),
                ("Symbol", "EURUSD"),
            )
        )
        self.assertEqual(
            str(subject), "AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD"
        )

    def test_GBPJPY_subject_to_string(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "GBP"),
                ("Quantity", "10000.00"),
                ("Symbol", "GBPJPY"),
            )
        )
        self.assertEqual(
            str(subject), "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
        )


class TestSubjectRepr(TestCase):
    def test_EURUSD_subject_repr(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "EUR"),
                ("Quantity", "10000.00"),
                ("Symbol", "EURUSD"),
            )
        )
        self.assertEqual(
            repr(subject),
            "Subject(AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD)",
        )

    def test_GBPJPY_subject_repr(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "GBP"),
                ("Quantity", "10000.00"),
                ("Symbol", "GBPJPY"),
            )
        )
        self.assertEqual(
            repr(subject),
            "Subject(AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY)",
        )


class TestCreateSubjectFromDict(TestCase):
    def test_dict_conversion(self):
        subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "EUR"),
                ("Quantity", "10000.00"),
                ("Symbol", "EURUSD"),
            )
        )
        self.assertEqual(
            str(subject), "AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD"
        )

    def test_dict_conversion_with_sorting(self):
        subject = Subject.from_dict(
            {
                "Currency": "EUR",
                "Quantity": "10000.00",
                "AssetClass": "Fx",
                "Symbol": "EURUSD",
            }
        )
        self.assertEqual(
            str(subject), "AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD"
        )


class TestSubjectEquality(TestCase):
    def setUp(self):
        self.component_map = {
            "Level": "1",
            "Exchange": "LSE",
            "AssetClass": "Equity",
            "Symbol": "BARC",
        }
        self.subject = Subject.from_dict(self.component_map)

    def test_subject_matches_its_clone(self):
        subject2 = Subject.from_dict(self.component_map)
        self.assertTrue(self.subject == subject2)

    def test_subject_matches_subject_parsed_from_its_string(self):
        subject2 = Subject.parse_string(str(self.subject))
        self.assertTrue(self.subject == subject2)

    def test_subject_does_not_matches_different_subject(self):
        subject2 = Subject.parse_string(
            "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
        )
        self.assertFalse(self.subject == subject2)

    def test_subject_does_not_matche_its_string(self):
        subject2 = "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
        self.assertFalse(self.subject == subject2)


class TestParseSubjectFromString(TestCase):
    def test_parsed_subject(self):
        subject = Subject.parse_string(
            "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
        )
        self.assertEqual(len(subject), 4)
        self.assertEqual(subject["AssetClass"], "Fx")
        self.assertEqual(subject["Symbol"], "GBPJPY")

    def test_parsed_subject_to_string_gives_back_equivalent_string(self):
        s = "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
        subject = Subject.parse_string(s)
        self.assertEqual(str(subject), s)


class TestSubjectGetWithDefault(TestCase):
    def setUp(self):
        self.subject = Subject(
            (
                ("AssetClass", "Future"),
                ("Exchange", "BMF"),
                ("Level", "1"),
                ("Source", "Reuters"),
                ("Symbol", "DDIF6"),
            )
        )

    def test_first_component_value(self):
        self.assertEqual(self.subject.get("AssetClass", "DEFAULT"), "Future")

    def test_level(self):
        self.assertEqual(self.subject.get("Level", "DEFAULT"), "1")

    def test_exchange(self):
        self.assertEqual(self.subject.get("Exchange", "DEFAULT"), "BMF")

    def test_last_component_value(self):
        self.assertEqual(self.subject.get("Symbol", "DEFAULT"), "DDIF6")

    def test_missing_component_returns_None(self):
        self.assertEqual(self.subject.get("Quantity", "DEFAULT"), "DEFAULT")


class TestSubjectIndexGet(TestCase):
    def setUp(self):
        self.subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "GBP"),
                ("Quantity", "1000.00"),
                ("Symbol", "GBPUSD"),
            )
        )

    def test_first_component_value(self):
        self.assertEqual(self.subject["AssetClass"], "Fx")

    def test_currency(self):
        self.assertEqual(self.subject["Currency"], "GBP")

    def test_quantity(self):
        self.assertEqual(self.subject["Quantity"], "1000.00")

    def test_last_component_value(self):
        self.assertEqual(self.subject["Symbol"], "GBPUSD")

    def test_missing_component_returns_None(self):
        self.assertEqual(self.subject["Exchange"], None)


class TestInOperatorWorksWithSubject(TestCase):
    def setUp(self):
        self.subject = Subject(
            (
                ("AssetClass", "Fx"),
                ("Currency", "CHF"),
                ("Quantity", "1000.00"),
                ("Symbol", "CHFUSD"),
            )
        )

    def test_first_component_is_in_subject(self):
        self.assertEqual("AssetClass" in self.subject, True)

    def test_middle_component_is_in_subject(self):
        self.assertEqual("Currency" in self.subject, True)

    def test_last_component_is_in_subject(self):
        self.assertEqual("Symbol" in self.subject, True)

    def test_missing_component_is_not_in_subject(self):
        self.assertEqual("Exchange" in self.subject, False)


class TestSubjectFlatten(TestCase):
    def test_flatten(self):
        self.assertListEqual(
            [
                "AssetClass",
                "Fx",
                "Currency",
                "GBP",
                "Quantity",
                "10000.00",
                "Symbol",
                "GBPJPY",
            ],
            Subject.parse_string(
                "AssetClass=Fx,Currency=GBP,Quantity=10000.00,Symbol=GBPJPY"
            ).flatten(),
        )
