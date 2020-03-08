#!/usr/bin/env python

import logging

from bidfx import Session, Subject, Field

"""
Example for subscription to Indicative FX level-1 subject and equity market depth.
"""


def on_price_event(event):
    if event.price:
        print(
            "LEVEL 1 {} {} / {}  {}".format(
                event.subject[Subject.CURRENCY_PAIR],
                event.price.get(Field.BID, ""),
                event.price.get(Field.ASK, ""),
                event.price.get(Field.BROKER, ""),
            )
        )


def on_price_grid_event(event):
    for row in event.grid:
        subject = row.subject
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

    for ccyPair in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"]:
        pricing.subscribe(
            pricing.build.fx.indicative.spot.currency_pair(ccyPair).create_subject()
        )

    src = "IDC"
    pricing.subscribe(
        pricing.build.equity.exchange("LSE")
        .level("Depth")
        .source(src)
        .symbol("E:VOD")
        .create_subject()
    )
    pricing.subscribe(
        pricing.build.equity.exchange("VTX")
        .level("Depth")
        .source(src)
        .symbol("E:ROG")
        .create_subject()
    )
    pricing.subscribe(
        pricing.build.equity.exchange("SWX")
        .level("Depth")
        .source(src)
        .symbol("E:ROSE")
        .create_subject()
    )
    pricing.subscribe(
        pricing.build.equity.exchange("SWX")
        .level("Depth")
        .source(src)
        .symbol("E:ALPH")
        .create_subject()
    )
    pricing.subscribe(
        pricing.build.equity.exchange("SWX")
        .level("Depth")
        .source(src)
        .symbol("E:CSLP")
        .create_subject()
    )


if __name__ == "__main__":
    main()
