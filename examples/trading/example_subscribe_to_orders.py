#!/usr/bin/env python

import logging
import time

from bidfx.session import Session


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    session = Session.create_from_ini_file()

    def message_listener(ws, message):
        print(message)

    def error_listener(ws, error):
        print(error)

    session.trading.subscribe_to_orders()
    session.trading.ws.add_message_listener(message_listener)
    session.trading.ws.add_error_listener(error_listener)
    session.trading.ws.start()

    time.sleep(2)

    session.trading.ws.stop()


if __name__ == "__main__":
    main()
