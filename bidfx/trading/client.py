__all__ = [
    "OrderFlow",
    "RESTTradeClient",
    "WSTradeClient",
    "ExecutionsSubscription",
    "IoiSubscription",
    "OrderSubscription",
]

import json
import logging
import multiprocessing as mp
from base64 import b64encode
from collections import OrderedDict
from queue import Empty
from threading import Thread
from typing import List

import requests
from websocket import WebSocketApp

from bidfx.trading.order import *
from bidfx.trading.order import OrderFields
from bidfx.trading.trade_error import TradeError

log = logging.getLogger("bidfx.trading.client")


def _create_basic_auth(username, password):
    """
    Encode authorisation header "username:password" as base 64.

    :param username: The username to encode.
    :param password: The password to encode.

    :return: The authorisation header.
    """
    auth = f"{username}:{password}"
    auth = b64encode(auth.encode()).decode("ascii")
    return f"Basic {auth}"


class OrderFlow:
    def __init__(self, url, request_queue):
        self.url = url
        self.request_queue = request_queue

    def stage_order(self, order: Order):
        """
        Stage FX Order

        :param order: FxOrder object
        """
        request = requests.Request(
            "POST", self.url, data=json.dumps([order.parameters])
        )
        self.request_queue.put(request)

    def stage_orders(self, orders: List[Order]):
        """
        Stage FX Orders

        :param orders: List of the FxOrder objects
        """
        data = json.dumps([order.parameters for order in orders])
        request = requests.Request("POST", self.url, data=data)
        self.request_queue.put(request)

    def query_orders(self, params: dict = None):
        """
        Query orders

        :param params: dict of query parameters

        :return: list of FxOrder objects
        """
        request = requests.Request("GET", self.url, params=params or {})
        self.request_queue.put(request)

    def query_single_order(self, order_ts_id: str):
        """
        Queries a single order.

        :param order_ts_id: uniquely identifies the order to fetch.

        :return: list of Order object
        """
        params = {OrderFields.ORDER_TS_ID.value: order_ts_id}
        self.query_orders(params=params)

    def amend(self, orders_ts_id: str, params: dict):
        """
        Amends an order.

        :param orders_ts_id: uniquely identifies the order.
        :param params: Parameters to amend
        """
        params.update({OrderFields.ORDER_TS_ID.value: orders_ts_id})
        request = requests.Request("POST", f"{self.url}/amend", data=json.dumps(params))
        self.request_queue.put(request)

    def cancel(self, orders_ts_id: str, reason: str):
        """
        Cancels an order.

        :param orders_ts_id: uniquely identifies the order.
        :param reason: Cancel reason
        """
        params = {
            OrderFields.ORDER_TS_ID.value: orders_ts_id,
            "reason": reason,
        }
        request = requests.Request(
            "POST", f"{self.url}/cancel", data=json.dumps(params)
        )
        self.request_queue.put(request)


class RESTTradeClient:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.headers = {
            "Authorization": _create_basic_auth(self.username, self.password),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.request_queue = mp.Queue()
        self.process = mp.Process(target=self._send_requests)
        self._running = mp.Event()
        self._running.set()
        self.response_listeners = []
        self.error_listeners = []

    @property
    def running(self) -> bool:
        """
        :return: `True` if session is running
        """
        return self._running.is_set()

    @property
    def base_url(self) -> str:
        return f"https://{self.host}:{self.port}"

    @property
    def fx(self) -> OrderFlow:
        return OrderFlow(f"{self.base_url}/api/om/v2/order", self.request_queue)

    def start(self):
        """
        Start the REST session.
        """
        self.process.start()

    def stop(self):
        """
        Stops the REST session.
        """
        self._running.clear()

    def _send_requests(self):
        """
        Sends requests from `requests_queue` if session is running
        """
        while self.running:
            try:
                request = self.request_queue.get(timeout=1)
                if request is not None:
                    self._send_one_request(request)
            except Empty as error:
                continue

    def _send_one_request(self, request):
        request.headers = self.headers
        log.info("sending request: {}".format(request))
        response = self.session.send(request.prepare())
        self._on_response(response)

    def _on_response(self, response: requests.Response):
        try:
            orders = response.json()
        except json.decoder.JSONDecodeError:
            error = TradeError.from_response(response)
            self._run_error_listeners(error)
        else:
            if isinstance(orders, list):
                if not len(orders):
                    error = TradeError.from_response(response)
                    self._run_error_listeners(error)
                    return
                self._run_response_listeners([Order(order) for order in orders])
            else:
                error_type = orders.get("type")
                message = orders.get("message")
                error = TradeError.from_string(error_type, message)
                self._run_error_listeners(error)

    def add_response_listener(self, listener):
        """
        Add listener which is called after getting a response
        
        :param listener: A listener function
        :type listener: def func(orders: List[FxOrder])
        """
        self.response_listeners.append(listener)

    def add_error_listener(self, listener):
        """
        Add listener which is called after getting an error
        
        :param listener: Function with signature: def func(error: TradeError)
        """
        self.error_listeners.append(listener)

    def _run_response_listeners(self, orders: List[Order]):
        """
        Runs the response listeners

        :param orders: Orders returned in response
        """
        for listener in self.response_listeners:
            listener(orders)

    def _run_error_listeners(self, error: TradeError):
        """
        Runs the error listeners
        :param error: instance of the `TradeError` subclass
        """
        for listener in self.error_listeners:
            listener(error)


class WSTradeClient(WebSocketApp):
    """
    Websocket client for subscribing to trading information.
    """

    def __init__(self, base_url, username, password):
        """

        :param base_url: The URL for the web socket.
        :param username: The client username.
        :param password: The client password.
        """
        self.message_listeners = []
        self.error_listeners = []
        self.url = self._full_url_with_path(base_url)
        header = {"Authorization": _create_basic_auth(username, password)}
        WebSocketApp.__init__(
            self,
            self.url,
            header,
            self.do_open,
            self.do_message,
            self.do_error,
            self.do_close,
        )
        self.message = None
        self.thread = None

    def start(self, message=None):
        """
        Starts the web socket session.

        :param message: The message to send.
        """
        self.message = message
        self.thread = Thread(target=self.run_forever)
        self.thread.start()

    def stop(self):
        self.close()

    def _full_url_with_path(self, url):
        return url

    def add_message_listener(self, listener):
        self.message_listeners.append(listener)

    def add_error_listener(self, listener):
        self.error_listeners.append(listener)

    @staticmethod
    def do_open(ws):
        """
        Function which is called at opening websocket.

        :param ws: WebSocketApp object
        """
        log.info("WebSocket opened")
        if ws.to_bytes:
            ws.send(ws.to_bytes.encode("utf-8"))

    @staticmethod
    def do_message(ws: "WSTradeClient", message):
        """
        Function which is called when received data.

        :param ws: WebSocketApp object
        :param message: utf-8 string which we get from the server.
        """
        message = json.loads(message, object_pairs_hook=OrderedDict)
        message = json.dumps(message, indent=4)
        for listener in ws.message_listeners:
            listener(ws, message)

    @staticmethod
    def do_error(ws, error):
        """
        Function which is called when we get error.

        :param ws: WebSocketApp object
        :param error: exception object.
        """
        log.error(str(error))
        for listener in ws.error_listeners:
            listener(ws, error)

    @staticmethod
    def do_close(ws):
        """
        Function which is called when closed the connection.

        :param ws: WebSocketApp object
        """
        log.info("WebSocket closed")


class ExecutionsSubscription(WSTradeClient):
    """
    Websocket client for subscribing to the executions stream
    """

    def _full_url_with_path(self, url):
        return url + "/api/om/v2/execution"


class IoiSubscription(WSTradeClient):
    """
    Websocket client for subscribing to the IOIs stream
    """

    def _full_url_with_path(self, url):
        return url + "/api/ioi/v1/ioi"


class OrderSubscription(WSTradeClient):
    """
    Websocket client for subscribing to the orders stream
    """

    def _full_url_with_path(self, url):
        return url + "/api/om/v2/order"
