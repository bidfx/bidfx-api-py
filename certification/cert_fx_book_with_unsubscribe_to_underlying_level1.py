#!/usr/bin/env python

import logging
import time

from bidfx import Session, Subject, Field, Tenor

""" Demonstrate subscription to 1 subject and Level-2 as multiple Level 1 subject.
After 20 seconds unsubscribe from some Level 1.
After 20 seconds unsubscribe from some Level 2.
After 30 seconds subscribe to new ones Level 1 subject.
"""


def on_price_event(event):
    subject = event.subject
    price_map = event.price
    if price_map:
        print(
            "LEVEL 1 {} {} {} {} {} {} -> {} / {}".format(
                subject[Subject.CURRENCY_PAIR],
                subject[Subject.LIQUIDITY_PROVIDER],
                subject[Subject.DEAL_TYPE],
                subject[Subject.TENOR],
                subject[Subject.CURRENCY],
                subject[Subject.QUANTITY],
                price_map.get(Field.BID, ""),
                price_map.get(Field.ASK, ""),
            )
        )


def on_price_grid_event(event):
    for row in event.grid:
        subject = event.subject
        bid_part = row.bid
        ask_part = row.ask
        row_number = 1
        for bid_price, ask_price in zip(bid_part, ask_part):
            print(
                "{} {} {} | BID {} {} | ASK {} {}".format(
                    row_number,
                    subject[Subject.CURRENCY_PAIR],
                    subject[Subject.DEAL_TYPE],
                    bid_price.get(Field.BID_FIRM, ""),
                    bid_price.get(Field.BID, ""),
                    ask_price.get(Field.ASK, ""),
                    ask_price.get(Field.ASK_FIRM, ""),
                )
            )
            row_number += 1
    print("=" * 10)


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
    pricing.callbacks.price_grid_event_fn = on_price_grid_event
    pricing.callbacks.subscription_event_fn = on_subscription_event
    pricing.callbacks.provider_event_fn = on_provider_event
    session.pricing.start()

    # Subscribe to next Level 2 subject
    for ccy_pair in ["EURUSD", "GBPUSD", "USDJPY"]:
        ccy = ccy_pair[:3]
        session.pricing.subscribe(
            session.pricing.build.fx.stream.spot.book()
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

    # Subscribe to next Level 1 subject
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

    time.sleep(20)

    # Unsubscribe from next Level 1 subject
    for lp in ["RBCFX", "SSFX", "MSFX", "CSFX", "JPMCFX"]:
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

    time.sleep(20)

    # Unsubscribe from next Level 2 subject
    for ccy_pair in ["EURUSD", "GBPUSD"]:
        ccy = ccy_pair[:3]
        session.pricing.unsubscribe(
            session.pricing.build.fx.stream.spot.book()
            .currency_pair(ccy_pair)
            .currency(ccy)
            .quantity(1000000)
            .create_subject()
        )

    time.sleep(30)

    # Subscribe to next Level 1 subject
    for lp in ["TSFX", "SGX"]:
        for ccy_pair in [
            "EURUSD",
        ]:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .create_subject()
            )


if __name__ == "__main__":
    main()
