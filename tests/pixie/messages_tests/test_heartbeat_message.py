import unittest

from bidfx.pricing._pixie.message.heartbeat_message import HeartbeatMessage
from bidfx.pricing._pixie.message.pixie_message_type import PixieMessageType
from bidfx.pricing._pixie.util.buffer_reads import read_byte


class TestHeartbeatMessage(unittest.TestCase):
    def setUp(self):
        self.heartbeat_message = "48"

    def test_heartbeat_message(self):
        heartbeat_message_bytes = bytearray.fromhex(self.heartbeat_message)
        self.assertEqual(
            read_byte(heartbeat_message_bytes), PixieMessageType.HeartbeatMessage
        )
        self.assertEqual(heartbeat_message_bytes, b"")

    def test_heartbeat_encode(self):
        heartbeat_message = HeartbeatMessage()
        self.assertEqual(heartbeat_message.to_bytes(), b"\x01H")
