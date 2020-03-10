#!/usr/bin/env python

import logging
import time

from bidfx import Session, Subject, Field, Tenor

"""
Example for Pixie subscription to 1 subject and after 10 seconds unsubscribe from some Level 1.
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

    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX", "JPMCFX"]:
        for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )

            session.pricing.subscribe(
                session.pricing.build.fx.stream.forward.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )

    time.sleep(10)

    print("Subscribe to new ones")
    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX"]:
        for ccy_pair in ["EURUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )

            session.pricing.subscribe(
                session.pricing.build.fx.stream.forward.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )

    time.sleep(10)

    print("Unsubscribe")
    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX"]:
        for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            session.pricing.unsubscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )

            session.pricing.unsubscribe(
                session.pricing.build.fx.stream.forward.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )

    time.sleep(10)

    print("Subscribe to new ones")
    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX", "JPMCFX"]:
        for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )

            session.pricing.subscribe(
                session.pricing.build.fx.stream.forward.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )


if __name__ == "__main__":
    main()
