import unittest

from bidfx.pricing._pixie.message.welcome_message import WelcomeMessage
from bidfx.pricing._pixie.util.buffer_reads import read_byte


class TestWelcomeMessage(unittest.TestCase):
    def setUp(self):
        self.welcome_message1_bytes = "570001000010e1000026ae"
        self.welcome_message2_bytes = "570701000010e1000026ae"

    def test_first_welcome_message(self):
        welcome_message_bytes = bytearray.fromhex(self.welcome_message1_bytes)
        self.assertEqual(read_byte(welcome_message_bytes), b"W")
        welcome_message = WelcomeMessage(welcome_message_bytes)
        self.assertEqual(welcome_message.options, 0)
        self.assertEqual(welcome_message.version, 1)
        self.assertEqual(welcome_message.client_id, 4321)
        self.assertEqual(welcome_message.server_id, 9902)

    def test_second_welcome_message(self):
        welcome_message_bytes = bytearray.fromhex(self.welcome_message2_bytes)
        self.assertEqual(read_byte(welcome_message_bytes), b"W")
        welcome_message = WelcomeMessage(welcome_message_bytes)
        self.assertEqual(welcome_message.options, 7)
        self.assertEqual(welcome_message.version, 1)
        self.assertEqual(welcome_message.client_id, 4321)
        self.assertEqual(welcome_message.server_id, 9902)
