#!/usr/bin/env python

import logging
from time import sleep

from bidfx import Session, Subject

"""
Example of streaming (RFS) firm spot rates direct from LPs.
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

    pricing.subscribe(
        pricing.build.fx.stream.spot.liquidity_provider("DBFX")
        .currency_pair("EURUSD")
        .currency("EUR")
        .quantity(1000000)
        .create_subject()
    )
    pricing.subscribe(
        pricing.build.fx.stream.spot.liquidity_provider("DBFX")
        .currency_pair("USDJPY")
        .currency("USD")
        .quantity(5000000)
        .create_subject()
    )

    sleep(60)

    pricing.stop()


if __name__ == "__main__":
    main()
