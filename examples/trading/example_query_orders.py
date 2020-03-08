#!/usr/bin/env python
import logging
from typing import List

from bidfx.session import Session
from bidfx.trading.order import Order
from bidfx.trading.trade_error import TradeError


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()

    def print_orders_callback(orders: List[Order]):
        for order in orders:
            print(order)
            session.trading.rest.stop()

    def print_error_info(error: TradeError):
        print(error)
        print(error.type)
        print(error.message)

    session.trading.rest.add_error_listener(print_error_info)
    session.trading.rest.add_response_listener(print_orders_callback)
    session.trading.rest.start()
    session.trading.ws.stop()

    session.trading.rest.fx.query_orders()


if __name__ == "__main__":
    main()
