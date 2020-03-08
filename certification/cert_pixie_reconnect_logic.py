#!/usr/bin/env python

import logging
import time
import socket
from threading import Thread

from bidfx import Session, Subject, Field

"""
Example of Pixie reconnect logic.
"""


def on_price_event(event):
    print(f"Price update to {event}")


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
        time.sleep(10)
        logging.error("** Killing the Pixie socket connection")
        session.pricing._pixie_provider._opened_socket.shutdown(socket.SHUT_RDWR)

    for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
        ccy = ccy_pair[:3]
        session.pricing.subscribe(
            session.pricing.build.fx.quote.spot.liquidity_provider("RBCFX")
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

    Thread(target=killer).start()


if __name__ == "__main__":
    main()
