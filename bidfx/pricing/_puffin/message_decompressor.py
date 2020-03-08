__all__ = ["MessageDecompressor"]

import io
import logging
import socket

from bidfx import PricingError
from .element import Element
from .token_dictionary import Dictionary, Token, TokenType

log = logging.getLogger("bidfx.pricing.puffin.decompression")

EMPTY_TOKEN = Token(TokenType.EMPTY)
NULL_VALUE_TOKEN = Token(TokenType.STRING)
NULL_CONTENT_TOKEN = Token(TokenType.CONTENT)


class MessageDecompressor:
    def __init__(self, opened_socket):
        self._dictionary = Dictionary()
        self._input = io.BufferedReader(socket.SocketIO(opened_socket, "r"), 4096)
        self._tag_stack = list()

    def decompress_message(self) -> Element:
        token = self._next_token()
        if token.type != TokenType.START:
            raise PricingError("start tag expected")
        element = Element(token.text)
        stack = list()
        while True:
            token = self._next_token()
            if token is None:
                raise PricingError("unexpected XML message termination")
            if token.type == TokenType.NAME:
                name = token
                value = self._next_token()
                if value is not None:
                    element.set(name.text, value.text)
            elif token.type == TokenType.END or token.type == TokenType.EMPTY:
                if len(stack) == 0:
                    return element
                element = stack.pop()
            elif token.type == TokenType.START:
                parent = element
                element = Element(token.text)
                parent.nest(element)
                stack.append(parent)
            elif token.type == TokenType.CONTENT:
                log.warning(f"ignoring unexpected XML content: {token}")
            elif token.type in (
                TokenType.INTEGER,
                TokenType.DOUBLE,
                TokenType.FRACTION,
                TokenType.STRING,
            ):
                raise PricingError(f"attribute value with no name: {token}")
            else:
                raise PricingError(f"unknown token type: {token}")

    def _next_token(self):
        b = self._read_byte()
        if Dictionary.is_first_byte_of_symbol(b):
            return self._parse_two_byte_token(b)
        if Dictionary.is_token_type(b):
            token_type = TokenType(b)
            if token_type == TokenType.END:
                return Token(TokenType.END, self._tag_stack.pop())
            if token_type == TokenType.EMPTY:
                return EMPTY_TOKEN
            return self._parse_unseen_token(token_type)
        else:
            raise PricingError("Puffin protocol syntax error: token tag expected")

    def _parse_two_byte_token(self, b1):
        symbol = Dictionary.first_byte_symbol(b1)
        b2 = self._input.peek(1)[0]
        if Dictionary.is_second_byte_of_symbol(b2):
            self._read_byte()
            symbol |= Dictionary.second_byte_symbol(b2)
        token = self._dictionary.get_token(symbol)
        if token.type == TokenType.START:
            self._tag_stack.append(token.text)
        return token

    def _parse_unseen_token(self, token_type):
        text_bytes = bytearray()
        while True:
            b = self._input.peek(1)[0]
            if Dictionary.is_plain_text(b):
                text_bytes.append(self._read_byte())
            else:
                if text_bytes:
                    text = text_bytes.decode("ascii")
                    token = Token(token_type, text)
                    if token_type == TokenType.START:
                        self._tag_stack.append(token)
                    self._dictionary.insert_token(token)
                    return token
                if token_type == TokenType.STRING:
                    return NULL_VALUE_TOKEN
                if token_type == TokenType.CONTENT:
                    return NULL_CONTENT_TOKEN
                raise PricingError("text of previously unseen token expected")

    def _read_byte(self):
        b = self._input.read(1)
        if b == b"":
            raise socket.error("end of socket stream")
        return ord(b)
