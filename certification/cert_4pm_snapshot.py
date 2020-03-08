#!/usr/bin/env python

import logging
from datetime import datetime
from decimal import Decimal

from bidfx import Session, Subject, Field

prices_by_subject = {}


def on_price_event(event):
    if (Field.BID in event.price) or (Field.ASK in event.price):
        full_price = merged_price(event)
        bid = full_price.get(Field.BID, "")
        ask = full_price.get(Field.ASK, "")
        if bid and ask:
            capture_price(event.subject, full_price, bid, ask)


def capture_price(subject, full_price, bid, ask):
    bid = Decimal(bid)
    ask = Decimal(ask)
    spread = ask - bid
    time_now = datetime.now().timestamp()
    origin_time = timestamp(full_price)
    print(
        "{} {} {} {} {} {} {} {} {} {} {} latency {}".format(
            datetime.utcfromtimestamp(time_now).isoformat(" ")[:-3],
            datetime.utcfromtimestamp(origin_time).isoformat(" ")[:-3],
            subject[Subject.CURRENCY_PAIR],
            subject[Subject.LIQUIDITY_PROVIDER],
            subject[Subject.DEAL_TYPE],
            subject[Subject.TENOR],
            subject[Subject.CURRENCY],
            subject[Subject.QUANTITY],
            bid,
            ask,
            spread,
            time_now - origin_time,
        )
    )


def timestamp(full_price):
    return float(full_price.get(Field.ORIGIN_TIME, "0")) / 1000


def merged_price(event):
    full_price = prices_by_subject.get(event.subject)
    if full_price is None:
        full_price = dict(event.price)
        prices_by_subject[event.subject] = full_price
    else:
        full_price.update(event.price)
    return full_price


def on_subscription_event(event):
    print(f"Subscription to {event.subject} is {event.status}")


def on_provider_event(event):
    print(f"Provider {event.provider} is {event.status}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file("~/.bidfx/api/tudor_prod_config.ini")
    pricing = session.pricing
    pricing.callbacks.price_event_fn = on_price_event
    pricing.callbacks.subscription_event_fn = on_subscription_event
    pricing.callbacks.provider_event_fn = on_provider_event
    session.pricing.start()

    PROVIDERS = {
        "SSFX",
        "DBFX",
    }
    SPOT_CCY_PAIRS = {
        "EURGBP",
    }

    for lp in PROVIDERS:
        for qty in list(map(lambda q: q * 1000000, (1, 5,))):
            for ccy_pair in SPOT_CCY_PAIRS:
                ccy = ccy_pair[:3]
                pricing.subscribe(
                    pricing.build.fx.quote.spot.liquidity_provider(lp)
                    .currency_pair(ccy_pair)
                    .currency(ccy)
                    .quantity(qty)
                    .create_subject()
                )


if __name__ == "__main__":
    main()
