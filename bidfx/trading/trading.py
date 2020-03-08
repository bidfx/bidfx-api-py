__all__ = ["TradingAPI"]

from configparser import ConfigParser

from .rest_trading import RestTradingAPI
from .ws_trading import WebSocketTradingAPI


class TradingAPI:
    """
    This class is the top-level API interface for accessing the trading services of BidFX.
    """

    def __init__(self, config_parser: ConfigParser):
        """
        :param config_parser: The API configuration settings.
        :type config_parser: configparser.ConfigParser
        """
        config_section = config_parser["Trading"]
        self._username = config_section["username"]
        self._rest = RestTradingAPI(config_section)
        self._ws = WebSocketTradingAPI(config_section)

    @property
    def rest(self) -> RestTradingAPI:
        """
        Gets the REST trading interface.

        :return: the `RestTradingAPI`
        """
        return self._rest

    @property
    def ws(self) -> WebSocketTradingAPI:
        """
        Gets the WebSocket trading interface.

        :return: the `WebSocketTradingAPI`
        """
        return self._ws

    @property
    def username(self) -> str:
        """
        Get the configured username used for sending trades.

        :return: The username.
        :rtype: str
        """
        return self._username

    # def subscribe_to_orders(self) -> 'TradingAPI':
    #     """
    #     Set current WebSocket client to `OrderSubscription`
    #     """
    #     self._ws = OrderSubscription(self._ws_base_url, self._username, self._password)
    #     return self
    #
    # def subscribe_to_iois(self) -> 'TradingAPI':
    #     self._ws = IoiSubscription(self._ws_base_url, self._username, self._password)
    #     return self
    #
    # def subscribe_to_executions(self) -> 'TradingAPI':
    #     """
    #     Set current WebSocket client to `ExecutionsSubscription`
    #     """
    #     self._ws = ExecutionsSubscription(self._ws_base_url, self._username, self._password)
    #     return self
