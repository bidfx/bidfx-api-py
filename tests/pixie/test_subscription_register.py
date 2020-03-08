from unittest import TestCase

from bidfx import Subject
from bidfx.pricing._pixie.subscription_register import SubscriptionRegister

SUBJECT1 = Subject.parse_string("Source=A,Symbol=EURGBP")
SUBJECT2 = Subject.parse_string("Source=A,Symbol=GBPAUD")
SUBJECT3 = Subject.parse_string("Source=A,Symbol=GBPUSD")
SUBJECT4 = Subject.parse_string("Source=A,Symbol=GBPNZD")
SUBJECT5 = Subject.parse_string("Source=A,Symbol=USDCAD")


class TestCurrentSubscriptionSet(TestCase):
    def setUp(self):
        self.register = SubscriptionRegister()

    def test_zero_subscribe(self):
        self.assertEqual(
            None, self.register.subscription_sync(), "No change to be synced"
        )

    def test_single_subscribe(self):
        self.register.subscribe(SUBJECT1)
        self.assertListEqual([SUBJECT1], self.register.subscription_sync().subjects)

    def test_sequence_of_subscribes(self):
        self.register.subscribe(SUBJECT1)
        self.register.subscribe(SUBJECT2)
        self.register.subscribe(SUBJECT3)
        self.assertListEqual(
            [SUBJECT1, SUBJECT2, SUBJECT3], self.register.subscription_sync().subjects
        )

    def test_sequence_of_subscribes_out_of_order(self):
        self.register.subscribe(SUBJECT3)
        self.register.subscribe(SUBJECT2)
        self.register.subscribe(SUBJECT5)
        self.register.subscribe(SUBJECT1)
        self.assertListEqual(
            [SUBJECT1, SUBJECT2, SUBJECT3, SUBJECT5],
            self.register.subscription_sync().subjects,
        )

    def test_subscribe_then_unsubscribe_one_subject(self):
        self.register.subscribe(SUBJECT1)
        self.register.unsubscribe(SUBJECT1)
        self.assertEqual(
            None, self.register.subscription_sync(), "no change to be synced"
        )

    def test_mix_subscribe_and_unsubscribe(self):
        self.register.subscribe(SUBJECT1)
        self.register.subscribe(SUBJECT2)
        self.register.subscribe(SUBJECT3)
        self.register.unsubscribe(SUBJECT2)
        self.register.subscribe(SUBJECT4)
        self.register.unsubscribe(SUBJECT3)
        self.register.subscribe(SUBJECT5)
        self.assertListEqual(
            [SUBJECT1, SUBJECT4, SUBJECT5], self.register.subscription_sync().subjects
        )

    def test_unsubscribe_when_not_present_is_not_an_error(self):
        self.register.unsubscribe(SUBJECT1)
        self.assertEqual(None, self.register.subscription_sync())
