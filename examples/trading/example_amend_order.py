#!/usr/bin/env python
import logging

from bidfx.session import Session
from bidfx.trading.order import Order
from bidfx.trading.trade_error import TradeError


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()
    INITIAL_QUANTITY = 5000
    AMENDED_QUANTITY = 10000

    def get_amend_callback():
        amended = False

        def amend_order(orders):
            nonlocal amended
            if amended:
                session.trading.rest.stop()
                return
            order_to_amend = orders[0]
            params = dict(
                reason="Arbitrary Amend Reason",
                quantity=AMENDED_QUANTITY,
                owner=session.trading.username,
                alternate_owner=session.trading.username,
            )
            session.trading.rest.fx.amend(order_to_amend.order_ts_id, params=params)
            amended = True

        return amend_order

    def print_orders_callback(orders):
        for order in orders:
            print("ORDER: {}".format(order))

    def print_error_callback(error: TradeError):
        print()
        print(error.type)
        print("ERROR: {}".format(error.message))

    session.trading.rest.add_response_listener(print_orders_callback)
    session.trading.rest.add_response_listener(get_amend_callback())
    session.trading.rest.add_error_listener(print_error_callback)

    session.trading.rest.start()
    session.trading.rest.fx.stage_order(
        Order(
            {
                "asset_class": "FX",
                "account": "FX_ACCT",
                "ccy_pair": "EURGBP",
                "deal_type": "SPOT",
                "tenor": "SPOT",
                "dealt_ccy": "GBP",
                "handling_type": "AUTOMATIC",
                "order_type": "MARKET",
                "price": 0.886865,
                "quantity": INITIAL_QUANTITY,
                "reference1": "SFPRef1",
                "reference2": "SFPRef2",
                "side": "SELL",
            }
        )
    )


if __name__ == "__main__":
    main()
