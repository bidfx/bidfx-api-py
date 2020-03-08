import unittest

from bidfx.pricing._pixie.message.grant_message import GrantMessage
from bidfx.pricing._pixie.util.buffer_reads import read_byte


class TestGrantMessage(unittest.TestCase):
    def setUp(self):
        self.granted_bytes = "477401"
        self.deny_bytes = "476614696e76616c69642063726564656e7469616c73"

    def test_granted_bytes(self):
        grant_message_bytes = bytearray.fromhex(self.granted_bytes)
        self.assertEqual(read_byte(grant_message_bytes), b"G")
        grant_message = GrantMessage(grant_message_bytes)
        self.assertEqual(grant_message.granted, b"t")

    def test_deny_bytes(self):
        grant_message_bytes = bytearray.fromhex(self.deny_bytes)
        self.assertEqual(read_byte(grant_message_bytes), b"G")
        grant_message = GrantMessage(grant_message_bytes)
        self.assertEqual(grant_message.granted, b"f")
        self.assertEqual(grant_message.reason, "invalid credentials")
