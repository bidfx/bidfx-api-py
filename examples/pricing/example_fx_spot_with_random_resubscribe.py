#!/usr/bin/env python

import logging
from random import shuffle
from time import sleep

from bidfx import Session, Subject

""" Example of streaming (RFS) firm spot rates direct from LPs.
"""


def on_price_event(event):
    if event.price:
        print(
            "{} {} {} {} {} -> {}".format(
                event.subject[Subject.CURRENCY_PAIR],
                event.subject[Subject.LIQUIDITY_PROVIDER],
                event.subject[Subject.DEAL_TYPE],
                event.subject[Subject.CURRENCY],
                event.subject[Subject.QUANTITY],
                event.price,
            )
        )


def on_subscription_event(event):
    print(f"Subscription to {event.subject} is {event.status}")


def on_provider_event(event):
    print(f"Provider {event.provider} is {event.status}")


def create_subjects(pricing):
    subjects = []
    for ccy_pair in [
        "EURUSD",
        "EURGBP",
        "GBPUSD",
        "GBPAUD",
        "GBPNZD",
        "USDCHF",
        "USDJPY",
        "USDCAD",
    ]:
        ccy = ccy_pair[:3]
        subjects.append(
            pricing.build.fx.stream.spot.liquidity_provider("CSFX")
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )
    return subjects


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
    subjects = create_subjects(pricing)

    for subject in subjects:
        pricing.subscribe(subject)
    for _ in range(10):
        sleep(2)
        shuffle(subjects)
        for subject in subjects[:3]:
            pricing.unsubscribe(subject)
        sleep(2)
        shuffle(subjects)
        for subject in subjects[:2]:
            pricing.subscribe(subject)

    sleep(20)
    pricing.stop()


if __name__ == "__main__":
    main()
