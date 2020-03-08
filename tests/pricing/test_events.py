from unittest import TestCase

from bidfx import Subject
from bidfx.pricing import (
    PriceEvent,
    SubscriptionEvent,
    SubscriptionStatus,
    ProviderEvent,
    ProviderStatus,
)

PROVIDER = "Pixie-3"
SUBJECT = Subject.parse_string(
    "AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD"
)
PRICE = {
    "AskSize": "1000000.0",
    "BidSize": "1000000.0",
    "Ask": "1.109271",
    "Bid": "1.107795",
}


class TestPriceEvent(TestCase):
    def test_get_subject(self):
        self.assertEqual(SUBJECT, PriceEvent(SUBJECT, PRICE, True).subject)

    def test_get_price(self):
        self.assertDictEqual(PRICE, PriceEvent(SUBJECT, PRICE, True).price)

    def test_get_price_is_true_when_there_are_fields(self):
        self.assertEqual(
            True, True if PriceEvent(SUBJECT, PRICE, True).price else False
        )

    def test_get_price_is_false_when_there_are_no_fields(self):
        self.assertEqual(False, True if PriceEvent(SUBJECT, {}, True).price else False)

    def test_get_full(self):
        self.assertEqual(True, PriceEvent(SUBJECT, PRICE, True).full)
        self.assertEqual(False, PriceEvent(SUBJECT, PRICE, False).full)

    def test_string_full(self):
        self.assertEqual(
            "PriceEvent AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD is "
            "{'AskSize': '1000000.0', 'BidSize': '1000000.0', 'Ask': '1.109271', 'Bid': '1.107795'} Full",
            str(PriceEvent(SUBJECT, PRICE, True)),
        )

    def test_string_partial(self):
        self.assertEqual(
            "PriceEvent AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD is "
            "{'AskSize': '1000000.0', 'BidSize': '1000000.0', 'Ask': '1.109271', 'Bid': '1.107795'} Partial",
            str(PriceEvent(SUBJECT, PRICE, False)),
        )

    def test_repr_full(self):
        self.assertEqual(
            "PriceEvent(Subject(AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD),"
            " Price({'AskSize': '1000000.0', 'BidSize': '1000000.0', 'Ask': '1.109271', 'Bid': '1.107795'})"
            " Full(True))",
            repr(PriceEvent(SUBJECT, PRICE, True)),
        )

    def test_repr_partial(self):
        self.assertEqual(
            "PriceEvent(Subject(AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD),"
            " Price({'AskSize': '1000000.0', 'BidSize': '1000000.0', 'Ask': '1.109271', 'Bid': '1.107795'})"
            " Full(False))",
            repr(PriceEvent(SUBJECT, PRICE, False)),
        )


class TestSubscriptionEvent(TestCase):
    def setUp(self):
        self.event = SubscriptionEvent(SUBJECT, SubscriptionStatus.STALE, "line down")

    def test_get_subject(self):
        self.assertEqual(SUBJECT, self.event.subject)

    def test_get_status(self):
        self.assertEqual(SubscriptionStatus.STALE, self.event.status)

    def test_get_explanation(self):
        self.assertEqual("line down", self.event.explanation)

    def test_string(self):
        self.assertEqual(
            "SubscriptionEvent AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD is STALE: line down",
            str(self.event),
        )

    def test_repr(self):
        self.assertEqual(
            "SubscriptionEvent(Subject(AssetClass=Fx,Currency=EUR,Quantity=10000.00,Symbol=EURUSD),"
            " <SubscriptionStatus.STALE: 3>, 'line down')",
            repr(self.event),
        )


class TestProviderEvent(TestCase):
    def setUp(self):
        self.event = ProviderEvent(
            PROVIDER, ProviderStatus.DOWN, "connection timed out"
        )

    def test_get_provider(self):
        self.assertEqual(PROVIDER, self.event.provider)

    def test_get_status(self):
        self.assertEqual(ProviderStatus.DOWN, self.event.status)

    def test_get_explanation(self):
        self.assertEqual("connection timed out", self.event.explanation)

    def test_string(self):
        self.assertEqual(
            "ProviderEvent Pixie-3 is DOWN: connection timed out", str(self.event)
        )

    def test_repr(self):
        self.assertEqual(
            "ProviderEvent('Pixie-3', <ProviderStatus.DOWN: 3>, 'connection timed out')",
            repr(self.event),
        )
