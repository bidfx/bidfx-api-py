__all__ = ["MessageCompressor"]

import logging

from .element import Element
from .token_dictionary import Dictionary, Token, TokenType

log = logging.getLogger("bidfx.pricing.puffin.compressor")


class MessageCompressor:
    def __init__(self, opened_socket):
        self._token_usage_by_token = {}
        self._dictionary = Dictionary(self._token_usage_by_token)
        self._opened_socket = opened_socket

    def compress_message(self, message: Element):
        # The only compressed messages the clients sends are single flat elements with string attributes.
        self.write_token(Token(TokenType.START, message.tag))
        for (name, value) in message.attributes():
            self.write_token(Token(TokenType.NAME, name))
            self.write_token(Token(TokenType.STRING, value))
        self._write_type(TokenType.EMPTY)

    def write_token(self, token: Token):
        if token.length():
            token_usage = self._token_usage_by_token.get(token)
            if token_usage is None:
                token_usage = self._dictionary.insert_token(token)
                if token_usage is not None:
                    self._token_usage_by_token[token] = token_usage
                self._write_type(token.type)
                self._opened_socket.sendall(token.text.encode("ascii"))
            else:
                self._write_token_usage(token_usage)
        else:
            self._write_type(token.type)

    def _write_type(self, token_type: TokenType):
        self._opened_socket.sendall(bytes([token_type.value]))

    def _write_token_usage(self, token_usage):
        symbol = self._dictionary.optimise_token_usage(token_usage)
        self._opened_socket.sendall(Dictionary.symbol_bytes(symbol))
