#!/usr/bin/env python
import logging

from bidfx import Session, Subject, Field

"""
Example for API Certification with FX spots.
"""


def on_price_event(event):
    subject = event.subject
    price_map = event.price
    if price_map:
        print(
            "LEVEL 1 {} {} {} {} {} -> {} / {}".format(
                subject[Subject.LIQUIDITY_PROVIDER],
                subject[Subject.DEAL_TYPE],
                subject[Subject.TENOR],
                subject[Subject.CURRENCY],
                subject[Subject.QUANTITY],
                price_map.get(Field.BID, ""),
                price_map.get(Field.ASK, ""),
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

    # Subscribe to next Level 1 subject
    for lp in ["RBCFX", "SSFX", "MSFX"]:
        ccy_pair = "EURUSD"
        ccy = "EUR"
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(5000000)
            .create_subject()
        )
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(20000000)
            .create_subject()
        )
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(100000000)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1234567.80)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1234567.89)
            .create_subject()
        )
        ccy = "USD"
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1234567.89)
            .create_subject()
        )

        ccy_pair = "USDJPY"
        ccy = "USD"
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(100000000)
            .create_subject()
        )

        ccy = "JPY"
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(100000000)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000000)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(10000000000)
            .create_subject()
        )

        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.liquidity_provider(lp)
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(12345678901)
            .create_subject()
        )


if __name__ == "__main__":
    main()
