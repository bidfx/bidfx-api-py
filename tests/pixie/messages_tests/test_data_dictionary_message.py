import unittest

from bidfx.pricing._pixie.message.data_dictionary_message import DataDictionaryMessage
from bidfx.pricing._pixie.message.pixie_message_type import PixieMessageType
from bidfx.pricing._pixie.util.buffer_reads import (
    read_double_fixed8,
    read_long_fixed8,
    read_byte,
)
from bidfx.pricing._pixie.util.compression import Compressor, Decompressor
from bidfx.pricing._pixie.util.varint import decode_varint, decode_zigzag


class TestDataDictionaryMessage(unittest.TestCase):
    def setUp(self):
        self.data_dictionary_message1_bytes = "4400090044560604426964014456060441736b024c56000842696453697a65034c56000841736b53697a65044c56000842696454696d65054c56000841736b54696d65064456020e4f726465725175616e7469747909445a040a4e65744368616e67650a445a020e50657263656e744368616e6765"
        self.data_dictionary_message2_bytes = "4402090044560604426964014456060441736b024c56000842696453697a65034c56000841736b53697a65044c56000842696454696d65054c56000841736b54696d65064456020e4f726465725175616e7469747909445a040a4e65744368616e67650a445a020e50657263656e744368616e6765"
        self.compressor = Compressor()
        self.decompressor = Decompressor()

        self.data_dict_data = [
            {
                "fid": 0,
                "type": read_double_fixed8,
                "encoding": decode_varint,
                "scale": 6,
                "name": "Bid",
                "enabled": True,
            },
            {
                "fid": 1,
                "type": read_double_fixed8,
                "encoding": decode_varint,
                "scale": 6,
                "name": "Ask",
                "enabled": True,
            },
            {
                "fid": 2,
                "type": read_long_fixed8,
                "encoding": decode_varint,
                "scale": 0,
                "name": "BidSize",
                "enabled": True,
            },
            {
                "fid": 3,
                "type": read_long_fixed8,
                "encoding": decode_varint,
                "scale": 0,
                "name": "AskSize",
                "enabled": True,
            },
            {
                "fid": 4,
                "type": read_long_fixed8,
                "encoding": decode_varint,
                "scale": 0,
                "name": "BidTime",
                "enabled": True,
            },
            {
                "fid": 5,
                "type": read_long_fixed8,
                "encoding": decode_varint,
                "scale": 0,
                "name": "AskTime",
                "enabled": True,
            },
            {
                "fid": 6,
                "type": read_double_fixed8,
                "encoding": decode_varint,
                "scale": 2,
                "name": "OrderQuantity",
                "enabled": True,
            },
            {
                "fid": 9,
                "type": read_double_fixed8,
                "encoding": decode_zigzag,
                "scale": 4,
                "name": "NetChange",
                "enabled": True,
            },
            {
                "fid": 10,
                "type": read_double_fixed8,
                "encoding": decode_zigzag,
                "scale": 2,
                "name": "PercentChange",
                "enabled": True,
            },
        ]

    def test_first_data_dictionary_message(self):
        data_dictionary_bytes = bytearray.fromhex(self.data_dictionary_message1_bytes)
        self.assertEqual(
            read_byte(data_dictionary_bytes), PixieMessageType.DataDictionaryMessage
        )
        data_dict = DataDictionaryMessage(data_dictionary_bytes, self.compressor)

        self.assertListEqual(
            self.data_dict_data, [i.__dict__ for i in data_dict.definitions]
        )
        self.assertEqual(data_dict.is_updated, False)
        self.assertEqual(data_dict.is_compressed, False)

    def test_second_welcome_message(self):
        data_dictionary_bytes = bytearray.fromhex(self.data_dictionary_message2_bytes)
        self.assertEqual(
            read_byte(data_dictionary_bytes), PixieMessageType.DataDictionaryMessage
        )
        data_dict = DataDictionaryMessage(data_dictionary_bytes, self.decompressor)
        self.assertEqual(data_dict.is_updated, True)

    def test_compressed_data_dictionary(self):
        bytes_message = bytearray.fromhex(self.data_dictionary_message2_bytes)
        header = bytearray(b"D\x03\t")  # Update + compressed
        body = bytes_message[3:]
        compressed_body = self.compressor.compress(body)
        compressed_data_dict_message = header + compressed_body
        self.assertEqual(
            read_byte(compressed_data_dict_message),
            PixieMessageType.DataDictionaryMessage,
        )
        data_dict = DataDictionaryMessage(
            compressed_data_dict_message, self.decompressor
        )
        self.assertListEqual(
            self.data_dict_data, [i.__dict__ for i in data_dict.definitions]
        )
        self.assertEqual(data_dict.is_updated, True)
        self.assertEqual(data_dict.is_compressed, True)
