__all__ = ["Dictionary", "Token", "TokenType"]

import io
import logging
import socket
from enum import Enum, unique

from bidfx import PricingError
from .element import Element

log = logging.getLogger("bidfx.pricing.puffin.decompressor")


@unique
class TokenType(Enum):
    END = 0
    EMPTY = 1
    START = 2
    CONTENT = 3
    NAME = 4
    INTEGER = 5
    DOUBLE = 6
    FRACTION = 7
    STRING = 8


class Token:
    __slots__ = ("type", "text")

    def __init__(self, token_type, text=None):
        self.type = token_type
        self.text = text

    def __str__(self):
        if self.type == TokenType.START:
            return f"<{self.text}>"
        if self.type == TokenType.END:
            return f"</{self.text}>"
        if self.type == TokenType.NAME:
            return f"{self.text}="
        if self.type == TokenType.EMPTY:
            return f"<{self.text} />"
        if self.type == TokenType.CONTENT:
            return self.text
        return f'="{self.text}"'

    def __key(self):
        return self.type, self.text

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.__key() == other.__key()
        return NotImplemented

    def length(self):
        return len(self.text) if self.text else 0


class TokenUsage:
    __slots__ = ("token", "symbol", "count")

    def __init__(self, token, symbol):
        self.token = token
        self.symbol = symbol
        self.count = 0

    def __str__(self):
        return f"TokenUsage({self.token} symbol={self.symbol} count={self.count})"


class GrowingList(list):
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None] * (index + 1 - len(self)))
        list.__setitem__(self, index, value)


class Dictionary:
    NUM_TOKEN_TYPES = len(TokenType)
    SYMBOL_BITS = 7
    SYMBOL_BIT = 1 << SYMBOL_BITS
    SYMBOL_MASK = SYMBOL_BIT - 1
    NUM_ONE_BYTE_SYMBOLS = SYMBOL_BIT
    MAX_SYMBOL = (NUM_ONE_BYTE_SYMBOLS - NUM_TOKEN_TYPES) << SYMBOL_BITS

    def __init__(self, token_usage_by_token: dict = None):
        self._next_symbol = 0
        self._winning_post = 0
        self._token_usage_by_symbol = GrowingList()
        self._token_usage_by_token = token_usage_by_token

    def get_token(self, symbol: int) -> Token:
        if 0 <= symbol < self._next_symbol:
            token_usage = self._token_usage_by_symbol[symbol]
            if token_usage:
                self.optimise_token_usage(token_usage)
                return token_usage.token
        raise PricingError("Puffin protocol syntax error: no token for symbol {symbol}")

    def optimise_token_usage(self, token_usage: TokenUsage) -> int:
        token_usage.count += 1
        if token_usage.symbol >= Dictionary.NUM_ONE_BYTE_SYMBOLS:
            if token_usage.count > self._winning_post:
                count = token_usage.count
                for symbol in range(Dictionary.NUM_ONE_BYTE_SYMBOLS):
                    swap = self._token_usage_by_symbol[symbol]
                    if count > swap.count:
                        self._token_usage_by_symbol[token_usage.symbol] = swap
                        swap.symbol = token_usage.symbol
                        self._token_usage_by_symbol[symbol] = token_usage
                        token_usage.symbol = symbol
                        return swap.symbol  # must use the old symbol!
                self._winning_post = count
        return token_usage.symbol

    def insert_token(self, token: Token) -> TokenUsage:
        token_usage = None
        if self._token_space_available():
            token_usage = self._add_token(token)
        else:
            self._purge_dictionary()
            if self._token_space_available():
                token_usage = self._add_token(token)
        return token_usage

    def _add_token(self, token: Token) -> TokenUsage:
        symbol = self._next_symbol
        token_usage = TokenUsage(token, symbol)
        self._next_symbol += 1
        self._token_usage_by_symbol[symbol] = token_usage
        return token_usage

    def _token_space_available(self) -> bool:
        return self._next_symbol < Dictionary.MAX_SYMBOL

    def _purge_dictionary(self):
        lower_quartile = self.estimate_lower_quartile()
        new_symbol = 0
        for old_symbol in range(Dictionary.MAX_SYMBOL):
            if self._token_usage_by_symbol[old_symbol].count > lower_quartile:
                if new_symbol < old_symbol:
                    token_usage = self._token_usage_by_symbol[old_symbol]
                    token_usage.symbol = new_symbol
                    self._token_usage_by_symbol[new_symbol] = token_usage
                new_symbol += 1
            else:
                if self._token_usage_by_token:
                    del self._token_usage_by_token[
                        self._token_usage_by_symbol[old_symbol].token
                    ]
                self._token_usage_by_symbol[old_symbol] = None
        self._next_symbol = new_symbol

    def estimate_lower_quartile(self) -> int:
        sample_count = 7
        step = Dictionary.MAX_SYMBOL // (sample_count + 1)
        if step == 0:
            return self._token_usage_by_symbol[Dictionary.MAX_SYMBOL // 2].count
        j = step - 1
        samples = list()
        for i in range(sample_count):
            samples.append(self._token_usage_by_symbol[j].count)
            j += step
        return sorted(samples)[sample_count // 4]

    @staticmethod
    def symbol_bytes(symbol: int) -> bytes:
        if symbol < Dictionary.NUM_ONE_BYTE_SYMBOLS:
            return bytes([Dictionary.SYMBOL_BIT | symbol])
        else:
            return bytes(
                [
                    Dictionary.SYMBOL_BIT | (symbol & Dictionary.SYMBOL_MASK),
                    (symbol >> Dictionary.SYMBOL_BITS) + Dictionary.NUM_TOKEN_TYPES,
                ]
            )

    @staticmethod
    def is_first_byte_of_symbol(b: int) -> bool:
        return (b & Dictionary.SYMBOL_BIT) != 0

    @staticmethod
    def is_second_byte_of_symbol(b: int) -> bool:
        return Dictionary.NUM_TOKEN_TYPES <= b < Dictionary.NUM_ONE_BYTE_SYMBOLS

    @staticmethod
    def is_plain_text(b: int) -> bool:
        return Dictionary.NUM_TOKEN_TYPES <= b < Dictionary.NUM_ONE_BYTE_SYMBOLS

    @staticmethod
    def is_token_type(b: int) -> bool:
        return (b & Dictionary.SYMBOL_MASK) < Dictionary.NUM_TOKEN_TYPES

    @staticmethod
    def first_byte_symbol(b: int) -> int:
        return b & Dictionary.SYMBOL_MASK

    @staticmethod
    def second_byte_symbol(b: int) -> int:
        return (b - Dictionary.NUM_TOKEN_TYPES) << Dictionary.SYMBOL_BITS
