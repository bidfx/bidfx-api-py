__all__ = ["Element", "ElementParser"]

from bidfx import PricingError

OMITTED_KEYS = ("Status", "SystemTime")


class Element:
    __slots__ = ("tag", "_attributes", "_sub_elements")

    def __init__(self, tag: str):
        self.tag = tag
        self._attributes = []
        self._sub_elements = []

    def nest(self, element):
        self._sub_elements.append(element)
        return self

    def set(self, name, value):
        self._attributes.append((name, value))
        return self

    def get(self, key, default):
        return self._find(key, (None, default))[1]

    def attributes(self) -> iter:
        return iter(self._attributes)

    def extract_price(self) -> dict:
        if self._sub_elements:
            return {
                k: v
                for k, v in self._sub_elements[0].attributes()
                if k not in OMITTED_KEYS
            }
        return {}

    def _find(self, key, default):
        return next((a for a in self._attributes if a[0] == key), default)

    def _attribute_str(self):
        return "".join([f' {kv[0]}="{kv[1]}"' for kv in self._attributes])

    def _sub_element_str(self):
        return "".join([str(e) for e in self._sub_elements])

    def __getitem__(self, key):
        return self._find(key, (None, None))[1]

    def __str__(self):
        if self._sub_elements:
            return f"<{self.tag}{self._attribute_str()}>{self._sub_element_str()}</{self.tag}>"
        return f"<{self.tag}{self._attribute_str()} />"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Element):
            return (
                self.tag == other.tag
                and self._attributes == other._attributes
                and self._sub_elements == other._sub_elements
            )
        return False


class ElementParser:
    def __init__(self, opened_socket):
        self._opened_socket = opened_socket

    def parse_element(self) -> Element:
        self._expect(b"<")
        tag, b = self._parse_text(b" /")
        element = Element(tag)
        if b == b" ":
            self._parse_attributes(element)
        self._expect(b">")
        return element

    def _parse_attributes(self, element: Element):
        b = self._read_byte()
        while b != b"/":
            name, _ = self._parse_text(b"=", b)
            self._expect(b'"')
            value, _ = self._parse_text(b'"')
            element.set(name, value)
            b = self._expect(b" ", b"/")
            if b == b" ":
                b = self._read_byte()

    def _expect(self, *expected):
        b = self._read_byte()
        if b not in expected:
            options = b"' or '".join(expected).decode("ascii")
            raise PricingError(f"expected '{options}' char while parsing XML element")
        return b

    def _parse_text(self, terminal: bytes, first: bytes = None):
        txt = bytearray()
        b = first or self._read_byte()
        while b not in terminal:
            txt.append(ord(b))
            b = self._read_byte()
        return txt.decode("ascii"), b

    def _read_byte(self):
        b = self._opened_socket.recv(1)
        if b == b"":
            raise PricingError("end of socket stream")
        return b
