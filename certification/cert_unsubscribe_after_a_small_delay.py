#!/usr/bin/env python

import logging
import time

from bidfx import Session, Subject, Field

""" Example subscription to a few spot subjects then after 10 seconds unsubscribe from some.
"""


def on_price_event(event):
    if event.price:
        print(
            "LEVEL 1 {} {} {} {} {} -> {} / {}".format(
                event.subject[Subject.CURRENCY_PAIR],
                event.subject[Subject.LIQUIDITY_PROVIDER],
                event.subject[Subject.DEAL_TYPE],
                event.subject[Subject.CURRENCY],
                event.subject[Subject.QUANTITY],
                event.price.get(Field.BID, ""),
                event.price.get(Field.ASK, ""),
            )
        )


def on_price_grid_event(event):
    for row in event.grid:
        subject = event.subject
        bid_part = row.bid
        ask_part = row.ask
        row_number = 1
        for bid_price, ask_price in zip(bid_part, ask_part):
            print(
                "LEVEL 2 {} {} {} | BID {} {} | ASK {} {}".format(
                    row_number,
                    subject[Subject.CURRENCY_PAIR],
                    subject[Subject.DEAL_TYPE],
                    bid_price.get(Field.BID_FIRM, ""),
                    bid_price.get(Field.BID, ""),
                    ask_price.get(Field.ASK, ""),
                    ask_price.get(Field.ASK_FIRM, ""),
                )
            )
            row_number += 1
    print("=" * 10)


def on_subscription_event(event):
    print(f"Subscription to {event.subject} is {event.status}")


def on_provider_event(event):
    print(f"Provider {event.provider} is {event.status}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()
    pricing = session.pricing
    pricing.callbacks.price_event_fn = on_price_event
    pricing.callbacks.price_grid_event_fn = on_price_grid_event
    pricing.callbacks.subscription_event_fn = on_subscription_event
    pricing.callbacks.provider_event_fn = on_provider_event
    session.pricing.start()

    for ccy_pair in [
        "EURUSD",
        "GBPUSD",
    ]:
        ccy = ccy_pair[:3]
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider("RBCFX")
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

    time.sleep(10)

    print("Subscribe to new ones")

    for ccy_pair in ["USDJPY"]:
        ccy = ccy_pair[:3]
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider("RBCFX")
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

    time.sleep(10)
    print("Unsubscribe to new ones")

    for ccy_pair in ["EURUSD", "GBPUSD"]:
        ccy = ccy_pair[:3]
        session.pricing.unsubscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider("RBCFX")
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )


if __name__ == "__main__":
    main()
