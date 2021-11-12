#!/usr/bin/env python

import logging
from time import sleep

from bidfx import Session, Subject, Field

"""
Example subscription to indicative FX level-1 subject from Puffin price service.
"""


def on_price_event(event):
    if event.price:
        print(
            "price update {} {}".format(
                event.subject[Subject.CURRENCY_PAIR], event.price
            )
        )


def on_subscription_event(event):
    print(f"Subscription to {event}")


def on_provider_event(event):
    print(f"Provider {event}")


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
    for ccyPair in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"]:
        pricing.subscribe(
            pricing.build.fx.indicative.spot.currency_pair(ccyPair).create_subject()
        )

    sleep(60)
    pricing.stop()


if __name__ == "__main__":
    main()
