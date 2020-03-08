#!/usr/bin/env python

import logging
import time
from threading import Thread

from bidfx import Session, Subject, Field

""" Example of Puffin reconnect logic.
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

    def killer():
        time.sleep(15)
        session.pricing._puffin_provider.sock.close()
        print("KILLER")

    for ccyPair in ["EURUSD", "GBPUSD", "USDJPY"]:
        session.pricing.subscribe(
            session.pricing.build.fx.indicative.spot.currency_pair(
                ccyPair
            ).create_subject()
        )

    Thread(target=killer).start()


if __name__ == "__main__":
    main()
