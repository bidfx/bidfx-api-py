import unittest

from bidfx.pricing._pixie.util.compression import Compressor, Decompressor


class TestCompression(unittest.TestCase):
    def setUp(self):
        self.compressor = Compressor()
        self.decompressor = Decompressor()

    def test_compression_reduces_data(self):
        text = "asd asdfsad gssfsg qwewqeqweqw sffsfdfsd asd asdfsad gssfsg qwewqeqweqw sffsfdfsd".encode(
            "ascii"
        )
        self.assertTrue(len(self.compressor.compress(text)) < len(text))

    def test_compress_decompress_are_the_same(self):
        text = "asd asdfsad gssfsg qwewqeqweqw sffsfdfsd asd asdfsad gssfsg qwewqeqweqw sffsfdfsd".encode(
            "ascii"
        )
        compressed = self.compressor.compress(text)
        decompressed = self.decompressor.decompress(compressed)
        self.assertEqual(decompressed, text)
