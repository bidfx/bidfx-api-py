#!/usr/bin/env python

import logging
import time

from bidfx.session import Session
from bidfx.trading.trade_error import TradeError


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()

    def print_orders_callback(orders):
        for order in orders:
            print(order)

    def print_error_callback(error: TradeError):
        print(error.type)
        print(error.message)

    session.trading.rest.add_response_listener(print_orders_callback)
    session.trading.rest.add_error_listener(print_error_callback)
    session.trading.rest.start()
    session.trading.ws.stop()

    for i in range(5):
        if i == 3:
            session.trading.rest.stop()
        time.sleep(1)
        session.trading.rest.fx.query_single_order("20200102-104300-3625828480-319-API")


if __name__ == "__main__":
    main()
