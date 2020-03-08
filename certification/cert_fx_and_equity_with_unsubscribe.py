#!/usr/bin/env python

import logging
import time

from bidfx import Session, Subject, Field

""" Example for Puffin subscription to indicative FX Level 1 subject and to equity market depth from ComStock.
Unsubscribe after 15 seconds from Level 2 subject
"""


def on_price_event(event):
    if event.price:
        print(
            "LEVEL 1 PUFFIN {} {} / {}  {}".format(
                event.subject[Subject.CURRENCY_PAIR],
                event.price.get(Field.BID, ""),
                event.price.get(Field.ASK, ""),
                event.price.get(Field.BROKER, ""),
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
                "LEVEL 2 {} {} | BID {} {} | ASK {} {}".format(
                    row_number,
                    subject[Subject.CURRENCY_PAIR],
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
    pricing.start()

    subject = pricing.build
    for ccyPair in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"]:
        pricing.subscribe(
            subject.fx.indicative.spot.currency_pair(ccyPair).create_subject()
        )

    vod = (
        subject.equity.exchange("LSE")
        .level("Depth")
        .source("ComStock")
        .symbol("E:VOD")
        .create_subject()
    )
    rog = (
        subject.equity.exchange("VTX")
        .level("Depth")
        .source("ComStock")
        .symbol("E:ROG")
        .create_subject()
    )

    pricing.subscribe(vod)
    pricing.subscribe(rog)

    time.sleep(25)
    pricing.unsubscribe(vod)

    time.sleep(25)
    pricing.subscribe(vod)


if __name__ == "__main__":
    main()
