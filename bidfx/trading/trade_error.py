__all__ = ["TradeError"]

from enum import Enum, auto

import requests

from bidfx.exceptions import TradingError


class TradeErrorType(Enum):
    UNAUTHORIZED = auto()
    BAD_REQUEST = auto()
    NOT_FOUND = auto()
    SERVER_ERROR = auto()
    UNKNOWN = auto()


class TradeError(TradingError):
    """
    The error that was received from the server
    """

    def __init__(self, error_type: TradeErrorType, message: str):
        self.type = error_type
        self.message = message

    @classmethod
    def from_string(cls, type_string, message):
        error_types_map = {
            "Unauthorized": TradeErrorType.UNAUTHORIZED,
            "Bad Request": TradeErrorType.BAD_REQUEST,
            "Not Found": TradeErrorType.NOT_FOUND,
        }

        error_type = error_types_map.get(type_string) or TradeErrorType.UNKNOWN
        return cls(error_type, message)

    @classmethod
    def from_response(cls, response: requests.Response):
        status_code_map = {
            401: TradeErrorType.UNAUTHORIZED,
            404: TradeErrorType.NOT_FOUND,
            500: TradeErrorType.SERVER_ERROR,
        }
        status_code = response.status_code
        error_type = status_code_map.get(status_code) or TradeErrorType.UNKNOWN
        return cls(error_type, "")
