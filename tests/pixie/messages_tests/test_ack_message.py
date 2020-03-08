import unittest

from bidfx.pricing._pixie.message.ack_message import AckMessage


class TestAckMessage(unittest.TestCase):
    def setUp(self):
        self.ack_message_bytes = "4187ad4be89997de9729b09b97de9729b19b97de97299a05"

    def test_ack_message(self):
        ack_message = AckMessage(1234567, 1415120801000, 1415120801200)
        ack_message.ack_time = 1415120801201
        ack_message.handling_time = 666
        self.assertEqual(
            ack_message.to_bytes()[1:], bytes.fromhex(self.ack_message_bytes)
        )

    def test_ack_handling_time(self):
        ack_message = AckMessage(1234567, 1415120801000, 1415120801200)
        ack_message.to_bytes()
        self.assertGreater(ack_message.price_received_time, ack_message.handling_time)
