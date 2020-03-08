__all__ = ["RestTradingAPI"]

import json
import logging
import multiprocessing as mp
from base64 import b64encode
from collections import OrderedDict
from queue import Empty
from threading import Thread
from typing import List

import requests as http
from websocket import WebSocketApp

log = logging.getLogger("bidfx.trading.rest")


def _create_basic_auth(username, password):
    auth = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {auth}"


class OrderFlow:
    def __init__(self, url, session):
        self._url = url
        self._session = session

    def create_order(self, order):
        """
        Creates a new order and stages it on the trading platform ready for trading.

        :param order: the order to create
        :type order: Order or dict
        """
        d = (
            order
            if isinstance(order, dict)
            else {k: v for k, v in order.__dict__.items() if v is not None}
        )
        return self._session.post(self._url, json=d)

    def get_order(self, order_id):
        log.info(f"requesting order ID: {order_id}")
        return self._session.get(
            self._url, params={"order_ts_id": order_id}, timeout=(3.05, 27)
        )

    # def cancel_order(self, order_id):
    #     return self._session.post(self._url, json=order)
    #
    # def amend_order(self, order_id):
    #     return self._session.post(self._url, json=order)


class RestTradingAPI:
    def __init__(self, config_section):
        host = config_section["host"]
        port = config_section.getint("port", 443)
        username = config_section["username"]
        password = config_section["password"]
        self._base_url = f"https://{host}:{port}/api"
        self._session = http.Session()
        self._session.trust_env = False
        self._session.auth = (username, password)

    def order(self, version=2):
        return OrderFlow(f"{self._base_url}/om/v{version}/order", self._session)

    def fx(self, version=2):
        return OrderFlow(f"{self._base_url}/om/v{version}/fx", self._session)

    # def stage_orders(self, orders: List[Order]):
    #     """
    #     Stage FX Orders
    #
    #     :param orders: List of the FxOrder objects
    #     """
    #     data = json.dumps([order.parameters for order in orders])
    #     request = requests.Request('POST', self.url, data=data)
    #     self.request_queue.put(request)
    #
    # def query_orders(self, params: dict = None):
    #     """
    #     Query orders
    #
    #     :param params: dict of query parameters
    #
    #     :return: list of FxOrder objects
    #     """
    #     request = requests.Request('GET', self.url, params=params or {})
    #     self.request_queue.put(request)
    #
    # def query_single_order(self, order_ts_id: str):
    #     """
    #     Queries a single order.
    #
    #     :param order_ts_id: uniquely identifies the order to fetch.
    #
    #     :return: list of Order object
    #     """
    #     params = {OrderFields.ORDER_TS_ID.value: order_ts_id}
    #     self.query_orders(params=params)
    #
    # def amend(self, orders_ts_id: str, params: dict):
    #     """
    #     Amends an order.
    #
    #     :param orders_ts_id: uniquely identifies the order.
    #     :param params: Parameters to amend
    #     """
    #     params.update({OrderFields.ORDER_TS_ID.value: orders_ts_id})
    #     request = requests.Request('POST', f'{self.url}/amend',
    #                                data=json.dumps(params))
    #     self.request_queue.put(request)
    #
    # def cancel(self, orders_ts_id: str, reason: str):
    #     """
    #     Cancels an order.
    #
    #     :param orders_ts_id: uniquely identifies the order.
    #     :param reason: Cancel reason
    #     """
    #     params = {
    #         OrderFields.ORDER_TS_ID.value: orders_ts_id,
    #         'reason': reason,
    #     }
    #     request = requests.Request('POST', f'{self.url}/cancel',
    #                                data=json.dumps(params))
    #     self.request_queue.put(request)
