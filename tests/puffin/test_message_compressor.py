import unittest

from bidfx.pricing._puffin.message_compressor import MessageCompressor
from bidfx.pricing._puffin.element import Element


class DummySocket:
    def __init__(self):
        self._collection = []

    def sendall(self, data):
        self._collection.append(data)
        return len(data)

    def collected(self):
        return b"".join(self._collection)


class TestCompression(unittest.TestCase):
    def setUp(self):
        self.opened_socket = DummySocket()
        self.compressor = MessageCompressor(self.opened_socket)

    def test_heartbeat(self):
        self.compressor.compress_message(Element("Heartbeat"))
        self.assertEqual(b"\x02Heartbeat\x01", self.opened_socket.collected())

    def test_multiple_heartbeats(self):
        self.compressor.compress_message(Element("Heartbeat"))
        self.compressor.compress_message(Element("Heartbeat"))
        self.compressor.compress_message(Element("Heartbeat"))
        self.assertEqual(
            b"\x02Heartbeat\x01\x80\x01\x80\x01", self.opened_socket.collected()
        )

    def test_status(self):
        self.compressor.compress_message(
            Element("Status")
            .set(
                "Subject",
                "AssetClass=Fx,Exchange=OTC,Level=1,Source=HSBC,Symbol=USDJPY",
            )
            .set("Id", "3")
            .set("Text", "some error")
        )
        self.assertEqual(
            b"\x02Status\x04Subject\x08AssetClass=Fx,Exchange=OTC,Level=1,Source=HSBC,Symbol=USDJPY"
            b"\x04Id\x083\x04Text\x08some error\x01",
            self.opened_socket.collected(),
        )

    def test_subscribe(self):
        self.compressor.compress_message(
            Element("Subscribe").set(
                "Subject",
                "AssetClass=Fx,Exchange=OTC,Level=1,Source=DBFX,Symbol=GBPUSD",
            )
        )
        self.assertEqual(
            b"\x02Subscribe\x04Subject\x08AssetClass=Fx,Exchange=OTC,Level=1,Source=DBFX,Symbol=GBPUSD\x01",
            self.opened_socket.collected(),
        )

    def test_multiple_subscribe_and_unsubscribe(self):
        subject = "AssetClass=Fx,Exchange=OTC,Level=1,Source=DBFX,Symbol=GBPUSD"
        self.compressor.compress_message(Element("Subscribe").set("Subject", subject))
        self.compressor.compress_message(Element("Subscribe").set("Subject", subject))
        self.compressor.compress_message(Element("Unsubscribe").set("Subject", subject))
        self.compressor.compress_message(Element("Subscribe").set("Subject", subject))
        self.compressor.compress_message(Element("Unsubscribe").set("Subject", subject))
        self.assertEqual(
            b"\x02Subscribe\x04Subject\x08AssetClass=Fx,Exchange=OTC,Level=1,Source=DBFX,Symbol=GBPUSD\x01"
            b"\x80\x81\x82\x01"
            b"\x02Unsubscribe\x81\x82\x01"
            b"\x80\x81\x82\x01"
            b"\x83\x81\x82\x01",
            self.opened_socket.collected(),
        )
