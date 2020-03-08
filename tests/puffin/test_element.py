import unittest

from bidfx import PricingError
from bidfx.pricing._puffin.element import Element, ElementParser


class TestGetElement(unittest.TestCase):
    def setUp(self):
        self.login = (
            Element("Login")
            .set("Name", "jbloggs")
            .set("Password", "secret")
            .set("Version", "8")
        )

    def test_get_first_attribute(self):
        self.assertEqual("jbloggs", self.login.get("Name", "XX"))

    def test_get_last_attribute(self):
        self.assertEqual("8", self.login.get("Version", "XX"))

    def test_get_middle_attribute(self):
        self.assertEqual("secret", self.login.get("Password", "XX"))

    def test_use_default_when_there_are_no_attributes(self):
        self.assertEqual("1000", Element("Heartbeat").get("Interval", "1000"))

    def test_use_default_when_not_present(self):
        self.assertEqual("1000", self.login.get("Interval", "1000"))
        self.assertEqual(
            "Source=Reuters,Symbol=A",
            self.login.get("Subject", "Source=Reuters,Symbol=A"),
        )


class TestToString(unittest.TestCase):
    def test_heartbeat(self):
        message = Element("Heartbeat")
        self.assertEqual("<Heartbeat />", str(message))

    def test_login(self):
        message = (
            Element("Login")
            .set("Name", "jbloggs")
            .set("Password", "secret")
            .set("Version", "8")
            .set("Description", "Python API")
            .set("Alias", "joe.bloggs")
        )
        self.assertEqual(
            '<Login Name="jbloggs" Password="secret" Version="8"'
            ' Description="Python API" Alias="joe.bloggs" />',
            str(message),
        )

    def test_grant(self):
        message = Element("Grant").set("Access", "false").set("Text", "access denied")
        self.assertEqual('<Grant Access="false" Text="access denied" />', str(message))

    def test_subscribe(self):
        message = Element("Subscribe").set(
            "Subject",
            "AssetClass=Fx,Exchange=OTC,Level=1,Source=Reuters,Symbol=EURGBP=",
        )
        self.assertEqual(
            '<Subscribe Subject="AssetClass=Fx,Exchange=OTC,Level=1,Source=Reuters,Symbol=EURGBP=" />',
            str(message),
        )

    def test_price_update(self):
        message = (
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
        self.assertEqual(
            '<Update Subject="AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32">'
            '<Price Bid="100.5" Ask="102.5" BidSize="1000" AskSize="3000" Name="Vodafone plc" /></Update>',
            str(message),
        )

    def test_price_status(self):
        message = (
            Element("Status")
            .set(
                "Subject",
                "AssetClass=Equity,Exchange=LSE,Level=1,Source=Bloomberg,Symbol=VOD LN",
            )
            .set("Id", "3")
            .set("Text", "Request times out")
        )
        self.assertEqual(
            '<Status Subject="AssetClass=Equity,Exchange=LSE,Level=1,Source=Bloomberg,Symbol=VOD LN"'
            ' Id="3" Text="Request times out" />',
            str(message),
        )


class TestEquals(unittest.TestCase):
    def setUp(self):
        self.login = (
            Element("Login")
            .set("Name", "jbloggs")
            .set("Password", "secret")
            .set("Version", "8")
        )
        self.update1 = (
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
        self.update2 = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            )
            .nest(
                Element("Price")
                .set("Bid", "100.6")
                .set("Ask", "102.7")
                .set("BidSize", "1000")
                .set("AskSize", "3000")
                .set("Name", "Vodafone plc")
            )
        )
        self.update3 = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A112345",
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

    def test_elements_equal_self(self):
        self.assertEqual(True, self.update1 == self.update1)
        self.assertEqual(True, self.update2 == self.update2)
        self.assertEqual(True, self.update3 == self.update3)

    def test_elements_not_equal_different(self):
        self.assertEqual(False, self.login == self.update1)
        self.assertEqual(False, self.login == self.update2)
        self.assertEqual(False, self.login == self.update3)
        self.assertEqual(False, self.update1 == self.update2)
        self.assertEqual(False, self.update1 == self.update3)
        self.assertEqual(False, self.update2 == self.update3)


class TestExtractPrice(unittest.TestCase):
    def test_extract_price(self):
        message = (
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
        price = message.extract_price()
        self.assertDictEqual(
            {
                "Bid": "100.5",
                "Ask": "102.5",
                "BidSize": "1000",
                "AskSize": "3000",
                "Name": "Vodafone plc",
            },
            price,
        )

    def test_extract_price_removes_status(self):
        message = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            )
            .nest(
                Element("Price")
                .set("Bid", "100.5")
                .set("Ask", "102.5")
                .set("Status", "OK")
                .set("BidSize", "1000")
                .set("AskSize", "3000")
            )
        )
        price = message.extract_price()
        self.assertDictEqual(
            {"Bid": "100.5", "Ask": "102.5", "BidSize": "1000", "AskSize": "3000"},
            price,
        )

    def test_extract_price_legacy_system_time(self):
        message = (
            Element("Update")
            .set(
                "Subject",
                "AssetClass=FixedIncome,Exchange=SGC,Level=1,Source=Lynx,Symbol=DE000A14KK32",
            )
            .nest(
                Element("Price")
                .set("Bid", "100.5")
                .set("Ask", "102.5")
                .set("SystemTime", "1582651285000")
                .set("BidSize", "1000")
                .set("AskSize", "3000")
            )
        )
        price = message.extract_price()
        self.assertDictEqual(
            {"Bid": "100.5", "Ask": "102.5", "BidSize": "1000", "AskSize": "3000"},
            price,
        )


class DummySocket:
    def __init__(self, bytes_):
        self.data = bytearray(bytes_)

    def recv(self, count):
        if self.data:
            data = self.data[:count]
            del self.data[:count]
            return data
        return b""


class TestElementParser(unittest.TestCase):
    def test_not_xml_element(self):
        with self.assertRaises(PricingError) as error:
            ElementParser(DummySocket(b"Hello")).parse_element()
        self.assertEqual(
            "expected '<' char while parsing XML element", str(error.exception)
        )

    def test_element_not_terminated(self):
        with self.assertRaises(PricingError) as error:
            ElementParser(
                DummySocket(b'<Subscribe Subject="Source=A,Symbol=B" /<<>>')
            ).parse_element()
        self.assertEqual(
            "expected '>' char while parsing XML element", str(error.exception)
        )

    def test_element_attribute_not_quoted(self):
        with self.assertRaises(PricingError) as error:
            ElementParser(DummySocket(b"<Subscribe Subject=Error />")).parse_element()
        self.assertEqual(
            """expected '"' char while parsing XML element""", str(error.exception)
        )

    def test_element_without_space_between_attributes(self):
        with self.assertRaises(PricingError) as error:
            ElementParser(
                DummySocket(b'<Subscribe A="OK"Error="Oops" />')
            ).parse_element()
        self.assertEqual(
            "expected ' ' or '/' char while parsing XML element", str(error.exception)
        )

    def test_stream_ends_midway_through_parsing_element(self):
        with self.assertRaises(PricingError) as error:
            ElementParser(DummySocket(b"<Help")).parse_element()
        self.assertEqual("end of socket stream", str(error.exception))

    def test_parse_heartbeat(self):
        parser = ElementParser(DummySocket(b"<Heartbeat />"))
        self.assertEqual(Element("Heartbeat"), parser.parse_element())

    def test_parse_heartbeat_compacted(self):
        parser = ElementParser(DummySocket(b"<Heartbeat/>"))
        self.assertEqual(Element("Heartbeat"), parser.parse_element())

    def test_parse_element_with_one_attribute(self):
        parser = ElementParser(
            DummySocket(b'<Subscribe Subject="Source=A,Symbol=B" />')
        )
        self.assertEqual(
            Element("Subscribe").set("Subject", "Source=A,Symbol=B"),
            parser.parse_element(),
        )

    def test_parse_element_with_one_attribute_compacted(self):
        parser = ElementParser(DummySocket(b'<Subscribe Subject="Source=A,Symbol=B"/>'))
        self.assertEqual(
            Element("Subscribe").set("Subject", "Source=A,Symbol=B"),
            parser.parse_element(),
        )

    def test_parse_element_with_one_attribute_with_spaces(self):
        parser = ElementParser(DummySocket(b'<Person Name="Joe A Bloggs" />'))
        self.assertEqual(
            Element("Person").set("Name", "Joe A Bloggs"), parser.parse_element()
        )

    def test_parse_element_with_two_attributes(self):
        parser = ElementParser(DummySocket(b'<Thing Size="23" Width="2" />'))
        self.assertEqual(
            Element("Thing").set("Size", "23").set("Width", "2"), parser.parse_element()
        )

    def test_parse_welcome(self):
        parser = ElementParser(
            DummySocket(
                b'<Welcome Encrypt="true" Ready="true" Time="1233360062625" Host="mausp651" Name="PublicPuffin" '
                b'ZipRequests="true" SessionKey="pb8ikgaormbx" ServerId="rdZdS8uFFL95reaeURdxCg" Port="9876" '
                b'Version="8" ZipPrices="true" Interval="60000" />'
            )
        )
        self.assertEqual(
            Element("Welcome")
            .set("Encrypt", "true")
            .set("Ready", "true")
            .set("Time", "1233360062625")
            .set("Host", "mausp651")
            .set("Name", "PublicPuffin")
            .set("ZipRequests", "true")
            .set("SessionKey", "pb8ikgaormbx")
            .set("ServerId", "rdZdS8uFFL95reaeURdxCg")
            .set("Port", "9876")
            .set("Version", "8")
            .set("ZipPrices", "true")
            .set("Interval", "60000"),
            parser.parse_element(),
        )

    def test_parse_multiple_elements(self):
        parser = ElementParser(
            DummySocket(
                b'<Heartbeat /><Subscribe Subject="Source=A,Symbol=B" /><Heartbeat Time="55" />'
            )
        )
        self.assertEqual(Element("Heartbeat"), parser.parse_element())
        self.assertEqual(
            Element("Subscribe").set("Subject", "Source=A,Symbol=B"),
            parser.parse_element(),
        )
        self.assertEqual(Element("Heartbeat").set("Time", "55"), parser.parse_element())
