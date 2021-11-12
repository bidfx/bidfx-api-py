#!/usr/bin/env python

import logging
import time

from bidfx import Session, Subject, Field

"""
Example for Puffin subscription to Indicative FX Level 1 subject.
Unsubscribe from all subject except one after 15 seconds.
Subscribe to new ones after 15 seconds.
"""


def on_price_event(event):
    subject = event.subject
    price_map = event.price
    if price_map:
        print(
            "LEVEL 1 indicative {} {} / {}  {}".format(
                subject[Subject.CURRENCY_PAIR],
                price_map.get(Field.BID, ""),
                price_map.get(Field.ASK, ""),
                price_map.get(Field.BROKER, ""),
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
    session.pricing.start()

    subjects = [
        session.pricing.build.fx.indicative.spot.currency_pair(ccyPair).create_subject()
        for ccyPair in ["EURUSD", "GBPUSD", "USDJPY", "USDCAD"]
    ]

    for s in subjects:
        session.pricing.subscribe(s)

    time.sleep(15)

    for s in subjects:
        session.pricing.unsubscribe(s)

    time.sleep(15)

    for s in subjects:
        session.pricing.subscribe(s)

    time.sleep(30)
    pricing.stop()


if __name__ == "__main__":
    main()
