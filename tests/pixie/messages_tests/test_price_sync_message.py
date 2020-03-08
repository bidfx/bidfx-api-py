import unittest

from bidfx.pricing._pixie.message.field_def_message import FieldDefMessage
from bidfx.pricing._pixie.message.pixie_message_type import PixieMessageType
from bidfx.pricing._pixie.message.price_sync_message import PriceSyncMessage
from bidfx.pricing._pixie.util.buffer_reads import read_long_fixed8, read_byte
from bidfx.pricing._pixie.util.compression import Compressor, Decompressor


class TestPriceSyncMessage(unittest.TestCase):
    def setUp(self):
        self.price_sync_compressed = "500103858afa8ee82c6337034a636061b0ffc100068c108a7b0793fd8f351c866a2f2b996122698c40655fb7b92e3c75a019aa8cfd0293fdd7eb5cb6058baf33c344d29858181c18c358242697ec812a139cc2e4c058f5d07d9d4835334c04000000ffff"
        self.price_sync_not_compressed = "500007b6b0b1e4f12c2f0403660004003ff8000000000000010000000000000bb8023ff8ac083126e979030000000000000bb8660104003ff5b645a1cac0830100000000000007d0023ff5d70a3d70a3d70300000000000007d06602040040015604189374bc0100000000000011940240017ae147ae147b030000000000001194"
        self.price_sync_with_status = "50010089effbb2eb2d00010a2a6608602c6604622620660662162066056236206607620e20e60c6004000000ffff"

        self.DATA_LIST = {
            0: FieldDefMessage(0, read_long_fixed8, None, 0, "SystemTime"),
            1: FieldDefMessage(1, read_long_fixed8, None, 0, "SystemLatency"),
            2: FieldDefMessage(2, read_long_fixed8, None, 0, "HopLatency1"),
            3: FieldDefMessage(3, read_long_fixed8, None, 0, "HopLatency2"),
        }
        self.compressor = Compressor()
        self.decompressor = Decompressor()

    def test_compressed_message(self):
        price_sync_message_bytes = bytearray.fromhex(self.price_sync_compressed)
        self.assertEqual(
            read_byte(price_sync_message_bytes), PixieMessageType.PriceSyncMessage
        )
        price_sync = PriceSyncMessage(price_sync_message_bytes, self.decompressor)
        self.assertEqual(price_sync.is_compressed, True)

        self.assertEqual(price_sync.revision, 3)
        self.assertEqual(price_sync.revision_time, 1539777135877)
        self.assertEqual(price_sync.conflation_latency, 99)
        self.assertEqual(55, price_sync.edition, 55)
        self.assertEqual(price_sync.size, 3)

    def test_not_compressed_message(self):
        price_sync_message_bytes = bytearray.fromhex(self.price_sync_not_compressed)
        self.assertEqual(
            read_byte(price_sync_message_bytes), PixieMessageType.PriceSyncMessage
        )
        price_sync = PriceSyncMessage(price_sync_message_bytes, self.decompressor)
        self.assertEqual(price_sync.is_compressed, False)

        self.assertEqual(price_sync.revision, 7)
        self.assertEqual(price_sync.revision_time, 1542372218934)
        self.assertEqual(price_sync.conflation_latency, 47)
        self.assertEqual(price_sync.edition, 4)
        self.assertEqual(price_sync.size, 3)

    def test_status_from_price_sync(self):
        price_sync_message_bytes = bytearray.fromhex(self.price_sync_with_status)
        self.assertEqual(
            read_byte(price_sync_message_bytes), PixieMessageType.PriceSyncMessage
        )
        price_sync = PriceSyncMessage(price_sync_message_bytes, self.decompressor)
        self.assertEqual(price_sync.is_compressed, True)
