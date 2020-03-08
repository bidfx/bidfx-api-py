#!/usr/bin/env python

import logging

from bidfx import Session, Subject, Field, Tenor

"""
Example for API subscribing to FX streaming forward _prices.
"""


def on_price_event(event):
    if event.price:
        print(
            "LEVEL 1 {} {} {} {} {} {} -> {} / {}".format(
                event.subject[Subject.CURRENCY_PAIR],
                event.subject[Subject.LIQUIDITY_PROVIDER],
                event.subject[Subject.DEAL_TYPE],
                event.subject[Subject.TENOR],
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
    pricing.start()

    for lp in ["RBCFX", "SSFX", "MSFX"]:
        for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            pricing.subscribe(
                pricing.build.fx.stream.forward.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )


if __name__ == "__main__":
    main()
