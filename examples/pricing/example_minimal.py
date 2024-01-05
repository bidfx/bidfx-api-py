#!/usr/bin/env python

from time import sleep
from bidfx import Session


def on_price_event(event):
    print(f"Price update to {event}")


def main():
    session = Session.create_from_ini_file()
    pricing = session.pricing
    pricing.callbacks.price_event_fn = on_price_event
    pricing.subscribe(
        pricing.build.fx.stream.spot.liquidity_provider("CSFX")
        .currency_pair("EURUSD")
        .currency("EUR")
        .quantity(1000000)
        .create_subject()
    )
    pricing.start()
    sleep(60)
    pricing.stop()


if __name__ == "__main__":
    main()
