#!/usr/bin/env python

import logging

from bidfx import Session, Subject, Field, Tenor

""" Example stress test with 1080 subscriptions.
WARNING: FOR TEST PURPOSES during API certification.
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

    # Subscribe to next Level 1 Quote subject

    PROVIDERS = {
        "UBSFX",
        "SSFX",
        "DBFX",
        "CITIFX",
        "NATIXISFX",
        "RBCFX",
        "TSFX2",
        "BOAFX",
        "TSFX",
        "CSFX",
        "GSFX",
        "SGX",
        "BARCFX",
        "JEFFX",
        "MSFX",
        "JPMCFX",
        "BNPFX",
    }
    CCY_PAIRS = {
        "EURGBP",
        "EURAUD",
        "EURCLF",
        "EURKWD",
        "EURBHD",
        "EUROMR",
        "EURJOD",
        "EURFKP",
        "EURGIP",
        "EURSHP",
        "EURKYD",
        "EURCHE",
        "EURCUC",
        "EURBSD",
        "EURPAB",
        "EURBMD",
        "EURCUP",
        "EURCHW",
        "EURSGD",
        "EURBND",
        "EURLYD",
        "EURAZN",
        "EURANG",
        "EURAWG",
        "EURBAM",
        "EURBGN",
        "EURBYN",
        "EURBBD",
        "EURBZD",
        "EURFJD",
        "EURTOP",
        "EURTND",
        "EURGEL",
        "EURWST",
        "EURXCD",
        "EURBRL",
        "EURPGK",
        "EURMXV",
        "EURPEN",
        "EURTMT",
        "EURQAR",
        "EURILS",
        "EURAED",
        "EURTRY",
        "EURSAR",
        "EURPLN",
        "EURGHS",
        "EURRON",
        "EURMYR",
        "EURSDG",
        "CLFKWD",
        "CLFBHD",
        "CLFOMR",
        "CLFJOD",
        "CLFFKP",
        "CLFGIP",
        "CLFSHP",
        "CLFKYD",
        "CLFCHE",
        "CLFCUC",
        "CLFBSD",
        "CLFPAB",
        "CLFBMD",
        "CLFCUP",
        "CLFCHW",
        "SGDBND",
        "SGDLYD",
        "SGDAZN",
        "SGDANG",
        "SGDAWG",
        "SGDBAM",
        "SGDBGN",
        "SGDBYN",
        "SGDBBD",
        "SGDBZD",
        "SGDFJD",
        "SGDTOP",
        "SGDTND",
        "SGDGEL",
        "SGDWST",
        "XCDBRL",
        "XCDPGK",
        "XCDMXV",
        "XCDPEN",
        "XCDTMT",
        "XCDQAR",
        "XCDILS",
        "XCDAED",
        "XCDTRY",
        "XCDSAR",
        "XCDPLN",
        "XCDGHS",
        "XCDRON",
        "XCDMYR",
        "XCDSDG",
    }

    for lp in PROVIDERS:
        for ccy_pair in CCY_PAIRS:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.quote.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1230080.11)
                .create_subject()
            )

        for ccy_pair in CCY_PAIRS:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.quote.ndf.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1230080.11)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )

    for lp in PROVIDERS:
        for ccy_pair in CCY_PAIRS:
            ccy = ccy_pair[:3]
            session.pricing.subscribe(
                session.pricing.build.fx.stream.spot.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1230080.11)
                .create_subject()
            )

            session.pricing.subscribe(
                session.pricing.build.fx.quote.ndf.liquidity_provider(lp)
                .currency_pair(ccy_pair)
                .currency(ccy)
                .quantity(1000000)
                .tenor(Tenor.of_month(1))
                .create_subject()
            )


if __name__ == "__main__":
    main()
