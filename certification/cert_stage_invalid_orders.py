#!/usr/bin/env python
import logging
import time
from typing import List

from bidfx import Session, Order, TradeError


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()

    def print_error_info(error: TradeError):
        print(error)
        print(error.type)
        print(error.message)

    def print_order(orders: List[Order]):
        for order in orders:
            print(order)
            print(order.errors)

    session.trading.rest.add_error_listener(print_error_info)
    session.trading.rest.add_response_listener(print_order)
    session.trading.rest.start()

    session.trading.rest.fx.stage_order(Order({}))
    session.trading.rest.fx.stage_order(
        Order(
            {
                "asset_class": "invalid",
                "account": "FX_ACCT",
                "ccy_pair": "EURGBP",
                "deal_type": "SPOT",
                "tenorr": "SPOT",  # the key is invalid
                "dealt_ccy": "GBP",
                "handling_type": "AUTOMATIC",
                "order_type": "MAKET",  # the value is invalid
                "price": 0.886865,
                "quantity": 500000,
                "reference1": "SFPRef1",
                "reference2": "SFPRef2",
                "side": "SELL",
            }
        )
    )

    time.sleep(5)
    session.trading.rest.stop()


if __name__ == "__main__":
    main()
