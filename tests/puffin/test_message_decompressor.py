import unittest

from bidfx.pricing._puffin.message_decompressor import MessageDecompressor
from bidfx.pricing._puffin.element import Element


class DummySocket:
    def __init__(self, *data):
        self.data = list(data)

    def recv_into(self, buffer):
        if self.data:
            data = self.data.pop(0)
            nbytes = len(data)
            buffer[0:nbytes] = data
            return nbytes
        return 0


class TestDecompression(unittest.TestCase):
    def test_heartbeat(self):
        opened_socket = DummySocket(b"\x02Heartbeat\x00")
        decompressor = MessageDecompressor(opened_socket)
        self.assertEqual(Element("Heartbeat"), decompressor.decompress_message())

    def test_status(self):
        opened_socket = DummySocket(
            b"\x02Status\x04Subject\x08AssetClass=Fx,Exchange=OTC,Level=1,Source=HSBC,Symbol=USDJPY",
            b"\x04Id\x063\x04Text\x08some error\x00",
        )
        decompressor = MessageDecompressor(opened_socket)
        self.assertEqual(
            Element("Status")
            .set(
                "Subject",
                "AssetClass=Fx,Exchange=OTC,Level=1,Source=HSBC,Symbol=USDJPY",
            )
            .set("Id", "3")
            .set("Text", "some error"),
            decompressor.decompress_message(),
        )

    def test_fragmented_single_price_update(self):
        opened_socket = DummySocket(
            b"\x02Update\x04Subject\x08AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            b"\x02Price\x04Bid\x06100.5\x04Ask\x06102.5\x04BidSize\x051000\x04AskSize\x053000",
            b"\x04Name\x08Vodafone plc\x01\x00",
        )
        decompressor = MessageDecompressor(opened_socket)
        expected = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            )
            .nest(
                Element("Price")
                .set("Bid", "100.5")
                .set("Ask", "102.5")
                .set("BidSize", "1000")
                .set("AskSize", "3000")
                .set("Name", "Vodafone plc")
            )
        )
        self.assertEqual(expected, decompressor.decompress_message())

    def test_repeat_price_update(self):
        opened_socket = DummySocket(
            b"\x02Update\x04Subject\x08AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            b"\x02Price\x04Bid\x06100.5\x04Ask\x06102.5\x04BidSize\x051000\x04AskSize\x053000",
            b"\x04Name\x08Vodafone plc\x01\x00"
            b"\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8A\x8B\x8C\x8D\x01\x00",
        )
        decompressor = MessageDecompressor(opened_socket)
        expected = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            )
            .nest(
                Element("Price")
                .set("Bid", "100.5")
                .set("Ask", "102.5")
                .set("BidSize", "1000")
                .set("AskSize", "3000")
                .set("Name", "Vodafone plc")
            )
        )
        self.assertEqual(expected, decompressor.decompress_message())
        self.assertEqual(expected, decompressor.decompress_message())

    def test_depth_price_update(self):
        opened_socket = DummySocket(
            b"\x02Set\x04Subject\x08AssetClass=Equity,Exchange=LSE,Level=Depth,Source=ComStock,Symbol=E:VOD"
            b"\x02Price\x04Name\x08Vodafone plc\x04Bid1\x06199\x04Ask1\x06"
            b"201\x04BidSize1\x05999\x04AskSize1\x051001\x04Bid2\x06198\x04Ask2\x06"
            b"202\x04BidSize2\x05998\x04AskSize2\x051002\x04Bid3\x06197\x04Ask3\x06"
            b"203\x04BidSize3\x05997\x04AskSize3\x051003\x04Bid4\x06196\x04Ask4\x06"
            b"204\x04BidSize4\x05996\x04AskSize4\x051004\x04Bid5\x06195\x04Ask5\x06"
            b"205\x04BidSize5\x05995\x04AskSize5\x051005\x04Bid6\x06194\x04Ask6\x06"
            b"206\x04BidSize6\x05994\x04AskSize6\x051006\x04Bid7\x06193\x04Ask7\x06"
            b"207\x04BidSize7\x05993\x04AskSize7\x051007\x04Bid8\x06192\x04Ask8\x06"
            b"208\x04BidSize8\x05992\x04AskSize8\x051008\x04Bid9\x06191\x04Ask9\x06"
            b"209\x04BidSize9\x05991\x04AskSize9\x051009\x01\x00"
        )
        decompressor = MessageDecompressor(opened_socket)
        expected = Element("Set").set(
            "Subject",
            "AssetClass=Equity,Exchange=LSE,Level=Depth,Source=ComStock,Symbol=E:VOD",
        )
        price = Element("Price").set("Name", "Vodafone plc")
        for i in range(1, 10):
            price.set(f"Bid{i}", str(200 - i))
            price.set(f"Ask{i}", str(200 + i))
            price.set(f"BidSize{i}", str(1000 - i))
            price.set(f"AskSize{i}", str(1000 + i))

        expected.nest(price)
        self.assertEqual(expected, decompressor.decompress_message())

    def test_set_depth_price_update_with_updates(self):
        opened_socket = DummySocket(
            b"\x02Set\x04Subject\x08AssetClass=Equity,Exchange=LSE,Level=Depth,Source=ComStoc"
            b"k,Symbol=E:VOD\x02Price\x04Name\x08Vodafone plc\x04Bid1\x06199\x04Ask1\x06"
            b"201\x04BidSize1\x05999\x04AskSize1\x051001\x04Bid2\x06198\x04Ask2\x06"
            b"202\x04BidSize2\x05998\x04AskSize2\x051002\x04Bid3\x06197\x04Ask3\x06"
            b"203\x04BidSize3\x05997\x04AskSize3\x051003\x04Bid4\x06196\x04Ask4\x06"
            b"204\x04BidSize4\x05996\x04AskSize4\x051004\x04Bid5\x06195\x04Ask5\x06"
            b"205\x04BidSize5\x05995\x04AskSize5\x051005\x04Bid6\x06194\x04Ask6\x06"
            b"206\x04BidSize6\x05994\x04AskSize6\x051006\x04Bid7\x06193\x04Ask7\x06"
            b"207\x04BidSize7\x05993\x04AskSize7\x051007\x04Bid8\x06192\x04Ask8\x06"
            b"208\x04BidSize8\x05992\x04AskSize8\x051008\x04Bid9\x06191\x04Ask9\x06"
            b"209\x04BidSize9\x05991\x04AskSize9\x051009\x04Bid10\x06190\x04Ask10\x06"
            b"210\x04BidSize10\x05990\x04AskSize10\x051010\x04Bid11\x06189\x04Ask11\x06"
            b"211\x04BidSize11\x05989\x04AskSize11\x051011\x04Bid12\x06188\x04Ask12\x06"
            b"212\x04BidSize12\x05988\x04AskSize12\x051012\x04Bid13\x06187\x04Ask13\x06"
            b"213\x04BidSize13\x05987\x04AskSize13\x051013\x04Bid14\x06186\x04Ask14\x06"
            b"214\x04BidSize14\x05986\x04AskSize14\x051014\x04Bid15\x06185\x04Ask15\x06"
            b"215\x04BidSize15\x05985\x04AskSize15\x051015\x04Bid16\x06184\x04Ask16\x06"
            b"216\x04BidSize16\x05984\x04AskSize16\x051016\x04Bid17\x06183\x04Ask17\x06"
            b"217\x04BidSize17\x05983\x04AskSize17\x051017\x04Bid18\x06182\x04Ask18\x06"
            b"218\x04BidSize18\x05982\x04AskSize18\x051018\x04Bid19\x06181\x04Ask19\x06"
            b"219\x04BidSize19\x05981\x04AskSize19\x051019\x04Bid20\x06180\x04Ask20\x06"
            b"220\x04BidSize20\x05980\x04AskSize20\x051020\x04Bid21\x06179\x04Ask21\x06"
            b"221\x04BidSize21\x05979\x04AskSize21\x051021\x04Bid22\x06178\x04Ask22\x06"
            b"222\x04BidSize22\x05978\x04AskSize22\x051022\x04Bid23\x06177\x04Ask23\x06"
            b"223\x04BidSize23\x05977\x04AskSize23\x051023\x04Bid24\x06176\x04Ask24\x06"
            b"224\x04BidSize24\x05976\x04AskSize24\x051024\x04Bid25\x06175\x04Ask25\x06"
            b"225\x04BidSize25\x05975\x04AskSize25\x051025\x04Bid26\x06174\x04Ask26\x06"
            b"226\x04BidSize26\x05974\x04AskSize26\x051026\x04Bid27\x06173\x04Ask27\x06"
            b"227\x04BidSize27\x05973\x04AskSize27\x051027\x04Bid28\x06172\x04Ask28\x06"
            b"228\x04BidSize28\x05972\x04AskSize28\x051028\x04Bid29\x06171\x04Ask29\x06"
            b"229\x04BidSize29\x05971\x04AskSize29\x051029\x01\x00\x02Update\x81\x82"
            b"\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91"
            b"\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0"
            b"\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf"
            b"\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe"
            b"\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd"
            b"\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc"
            b"\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb"
            b"\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
            b"\xfb\xfc\xfd\xfe\xff\x80\x0a\x81\x0a\x82\x0a\x83\x0a\x84\x0a\x85\x0a\x86\x0a"
            b"\x87\x0a\x88\x0a\x89\x0a\x8a\x0a\x8b\x0a\x8c\x0a\x8d\x0a\x8e\x0a\x8f\x0a\x90\x0a\x91"
            b"\x0a\x92\x0a\x93\x0a\x94\x0a\x95\x0a\x96\x0a\x97\x0a\x98\x0a\x99\x0a\x9a\x0a\x9b\x0a\x9c"
            b"\x0a\x9d\x0a\x9e\x0a\x9f\x0a\xa0\x0a\xa1\x0a\xa2\x0a\xa3\x0a\xa4\x0a\xa5\x0a\xa6\x0a\xa7"
            b"\x0a\xa8\x0a\xa9\x0a\xaa\x0a\xab\x0a\xac\x0a\xad\x0a\xae\x0a\xaf\x0a\xb0\x0a\xb1\x0a\xb2"
            b"\x0a\xb3\x0a\xb4\x0a\xb5\x0a\xb6\x0a\xb7\x0a\xb8\x0a\xb9\x0a\xba\x0a\xbb\x0a\xbc\x0a\xbd"
            b"\x0a\xbe\x0a\xbf\x0a\xc0\x0a\xc1\x0a\xc2\x0a\xc3\x0a\xc4\x0a\xc5\x0a\xc6\x0a\xc7\x0a\xc8"
            b"\x0a\xc9\x0a\xca\x0a\xcb\x0a\xcc\x0a\xcd\x0a\xce\x0a\xcf\x0a\xd0\x0a\xd1\x0a\xd2\x0a\xd3"
            b"\x0a\xd4\x0a\xd5\x0a\xd6\x0a\xd7\x0a\xd8\x0a\xd9\x0a\xda\x0a\xdb\x0a\xdc\x0a\xdd\x0a\xde"
            b"\x0a\xdf\x0a\xe0\x0a\xe1\x0a\xe2\x0a\xe3\x0a\xe4\x0a\xe5\x0a\xe6\x0a\xe7\x0a\xe8\x0a\xe9"
            b"\x0a\xea\x0a\xeb\x0a\xec\x0a\xed\x0a\x01\x00\xee\x0a\x81\x82\x83\x84\x85\x86"
            b"\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95"
            b"\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4"
            b"\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3"
            b"\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2"
            b"\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1"
            b"\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0"
            b"\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef"
            b"\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe"
            b"\xff\x80\x81\x0a\x82\x0a\x83\x0a\x84\x0a\x85\x0a\x86\x0a\x87\x0a\x88\x0a\x89\x0a\x8a"
            b"\x0a\x8b\x0a\x8c\x0a\x8d\x0a\x8e\x0a\x8f\x0a\x90\x0a\x91\x0a\x92\x0a\x93\x0a\x94\x0a\x95"
            b"\x0a\x96\x0a\x97\x0a\x98\x0a\x99\x0a\x9a\x0a\x9b\x0a\x9c\x0a\x9d\x0a\x9e\x0a\x9f\x0a\xa0"
            b"\x0a\xa1\x0a\xa2\x0a\xa3\x0a\xa4\x0a\xa5\x0a\xa6\x0a\xa7\x0a\xa8\x0a\xa9\x0a\xaa\x0a\xab"
            b"\x0a\xac\x0a\xad\x0a\xae\x0a\xaf\x0a\xb0\x0a\xb1\x0a\xb2\x0a\xb3\x0a\xb4\x0a\xb5\x0a\xb6"
            b"\x0a\xb7\x0a\xb8\x0a\xb9\x0a\xba\x0a\xbb\x0a\xbc\x0a\xbd\x0a\xbe\x0a\xbf\x0a\xc0\x0a\xc1"
            b"\x0a\xc2\x0a\xc3\x0a\xc4\x0a\xc5\x0a\xc6\x0a\xc7\x0a\xc8\x0a\xc9\x0a\xca\x0a\xcb\x0a\xcc"
            b"\x0a\xcd\x0a\xce\x0a\xcf\x0a\xd0\x0a\xd1\x0a\xd2\x0a\xd3\x0a\xd4\x0a\xd5\x0a\xd6\x0a\xd7"
            b"\x0a\xd8\x0a\xd9\x0a\xda\x0a\xdb\x0a\xdc\x0a\xdd\x0a\xde\x0a\xdf\x0a\xe0\x0a\xe1\x0a\xe2"
            b"\x0a\xe3\x0a\xe4\x0a\xe5\x0a\xe6\x0a\xe7\x0a\xe8\x0a\xe9\x0a\xea\x0a\xeb\x0a\xec\x0a\xed"
            b"\x0a\x01\x00"
        )
        decompressor = MessageDecompressor(opened_socket)
        price = Element("Price").set("Name", "Vodafone plc")
        for i in range(1, 30):
            price.set(f"Bid{i}", str(200 - i))
            price.set(f"Ask{i}", str(200 + i))
            price.set(f"BidSize{i}", str(1000 - i))
            price.set(f"AskSize{i}", str(1000 + i))

        subject = (
            "AssetClass=Equity,Exchange=LSE,Level=Depth,Source=ComStock,Symbol=E:VOD"
        )
        expected1 = Element("Set").set("Subject", subject).nest(price)
        expected2 = Element("Update").set("Subject", subject).nest(price)
        expected3 = Element("Update").set("Subject", subject).nest(price)
        self.assertEqual(expected1, decompressor.decompress_message())
        self.assertEqual(expected2, decompressor.decompress_message())
        self.assertEqual(expected3, decompressor.decompress_message())
