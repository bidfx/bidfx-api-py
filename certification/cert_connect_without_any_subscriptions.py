#!/usr/bin/env python

import logging

from bidfx import Session

""" Example without any price subscriptions to demonstrate that the session remains open.
"""


def on_provider_event(event):
    print(f"{event}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()
    session.pricing.callbacks.provider_event_fn = on_provider_event
    session.pricing.start()


if __name__ == "__main__":
    main()
