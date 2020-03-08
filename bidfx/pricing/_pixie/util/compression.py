import zlib


class Compressor:
    def __init__(self):
        self._zip = zlib.compressobj(6, zlib.DEFLATED, -zlib.MAX_WBITS)

    def compress(self, input_bytes):
        buf = self._zip.compress(input_bytes) + self._zip.flush(zlib.Z_SYNC_FLUSH)
        return bytearray(buf)


class Decompressor:
    def __init__(self):
        self._unzip = zlib.decompressobj(-zlib.MAX_WBITS)

    def decompress(self, input_bytes):
        buf = self._unzip.decompress(input_bytes) + self._unzip.flush()
        return bytearray(buf)
