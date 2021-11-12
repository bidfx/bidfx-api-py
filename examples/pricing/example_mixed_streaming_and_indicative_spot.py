#!/usr/bin/env python

import logging
from time import sleep

from bidfx import Session, Subject, Field

""" Example of mixed indicative FX spot _prices and streaming, dealable spot rates direct from LPs.
"""


def on_price_event(event):
    if event.price:
        if (
            event.subject[Subject.ASSET_CLASS] == "Fx"
            and Subject.EXCHANGE not in event.subject
        ):
            print(
                "LEVEL 1 quote {} {}/{} (LP={})".format(
                    event.subject[Subject.CURRENCY_PAIR],
                    event.price.get(Field.BID, ""),
                    event.price.get(Field.ASK, ""),
                    event.subject[Subject.LIQUIDITY_PROVIDER],
                )
            )
        else:
            print(
                "LEVEL 1 indi  {} {}/{} (Broker={})".format(
                    event.subject[Subject.CURRENCY_PAIR],
                    event.price.get(Field.BID, ""),
                    event.price.get(Field.ASK, ""),
                    event.price.get(Field.BROKER, "n/a"),
                )
            )


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
    pricing.callbacks.subscription_event_fn = on_subscription_event
    pricing.callbacks.provider_event_fn = on_provider_event
    pricing.start()

    for ccyPair in ["AUDUSD", "NZDUSD", "USDMXN"]:
        pricing.subscribe(
            pricing.build.fx.indicative.spot.currency_pair(ccyPair).create_subject()
        )

    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX", "JPMCFX"]:
        for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            pricing.subscribe(
                pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )

    sleep(60)
    pricing.stop()


if __name__ == "__main__":
    main()
