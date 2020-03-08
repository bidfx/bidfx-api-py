import unittest

from bidfx.pricing._pixie.control_operations import ControlOperations
from bidfx.pricing._pixie.message.pixie_message_type import PixieMessageType
from bidfx.pricing._pixie.message.subscription_sync_message import (
    SubscriptionSyncMessage,
)
from bidfx.pricing._pixie.util.buffer_reads import read_byte
from bidfx.pricing._pixie.util.compression import Decompressor
from bidfx.pricing._pixie.util.varint import decode_varint
from bidfx.pricing.subject import Subject


class TestSubscriptionSyncMessage(unittest.TestCase):
    def setUp(self):
        self.subjects = [
            Subject.parse_string("Quantity=2500000,Symbol=EURGBP"),
            Subject.parse_string("Quantity=5600000,Symbol=USDJPY"),
        ]

        self.price_sync_edition_sequence_number = 123
        self.decompressor = Decompressor()

    def test_subscription_sync_not_compressed_encode(self):
        subj_mess = SubscriptionSyncMessage(
            self.price_sync_edition_sequence_number,
            self.subjects,
            is_compressed=False,
            is_controls=False,
        )
        encoded_message = subj_mess.to_bytes()
        self.assertEqual(decode_varint(encoded_message), 68)
        self.assertEqual(
            bytearray(
                b"S\000\173\002\004\011Quantity\0102500000\007Symbol\007EURGBP\004\011Quantity\0105600000\007Symbol\007USDJPY"
            ),
            encoded_message,
        )

    def test_subscription_sync_encode_not_compressed_with_control_block(self):
        control_block = {0: ControlOperations.REFRESH, 1: ControlOperations.TOGGLE}
        subj_mess = SubscriptionSyncMessage(
            self.price_sync_edition_sequence_number,
            self.subjects,
            is_compressed=False,
            is_controls=True,
            sids=control_block,
        )

        encoded_message = subj_mess.to_bytes()
        self.assertEqual(decode_varint(encoded_message), 73)
        self.assertEqual(
            bytearray(
                b"S\002\173\002\004\011Quantity\0102500000\007Symbol\007EURGBP\004\011Quantity\0105600000\007Symbol\007USDJPY\002\000R\001T"
            ),
            encoded_message,
        )

    def test_subscription_sync_compressed_encode_without_control_block(self):
        subj_mess = SubscriptionSyncMessage(
            self.price_sync_edition_sequence_number, self.subjects, is_compressed=True
        )

        encoded_message = subj_mess.to_bytes()
        self.assertEqual(decode_varint(encoded_message), 59)
        self.assertEqual(
            read_byte(encoded_message), PixieMessageType.SubscriptionSyncMessage
        )
        self.assertEqual(decode_varint(encoded_message), 1)
        self.assertEqual(
            decode_varint(encoded_message), self.price_sync_edition_sequence_number
        )
        self.assertEqual(decode_varint(encoded_message), len(self.subjects))
        decompressed = self.decompressor.decompress(encoded_message)
        self.assertEqual(
            bytearray(
                b"\004\011Quantity\0102500000\007Symbol\007EURGBP\004\011Quantity\0105600000\007Symbol\007USDJPY"
            ),
            decompressed,
        )

    def test_subscription_sync_compressed_encode_with_control_block(self):
        control_block = {0: ControlOperations.REFRESH, 1: ControlOperations.TOGGLE}
        subj_mess = SubscriptionSyncMessage(
            self.price_sync_edition_sequence_number,
            self.subjects,
            is_compressed=True,
            is_controls=True,
            sids=control_block,
        )

        encoded_message = subj_mess.to_bytes()
        self.assertEqual(decode_varint(encoded_message), 70)
        self.assertEqual(
            read_byte(encoded_message), PixieMessageType.SubscriptionSyncMessage
        )
        self.assertEqual(decode_varint(encoded_message), 3)
        self.assertEqual(
            decode_varint(encoded_message), self.price_sync_edition_sequence_number
        )
        self.assertEqual(decode_varint(encoded_message), len(self.subjects))
        decompressed = self.decompressor.decompress(encoded_message)
        self.assertEqual(
            bytearray(
                b"\004\011Quantity\0102500000\007Symbol\007EURGBP\004\011Quantity\0105600000\007Symbol\007USDJPY\002\000R\001T"
            ),
            decompressed,
        )
