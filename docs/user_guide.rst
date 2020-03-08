**********
User Guide
**********

Download and installation
=========================

Python version
--------------

BidFX Python API works with Python 3.6 and greater. To check that your
have the right version of Python installed use the command:

.. code-block:: python

    python --version

You should get some output like ``Python 3.7.5``. 

If you do not have Python, please install the latest 3.x version from `python.org <https://python.org>`_
or refer to the `Installing Python <http://docs.python-guide.org/en/latest/starting/installation/>`_ section
of the Hitchhiker’s Guide to Python.


Git repository
--------------

As part of the *BidFX Open Source initiative*,
BidFX intend to published the source code for the Python API on the
`BidFX Github Page <https://github.com/bidfx>`_.
This source will be released soon.
When available, you will be able to clone the API with the following command.

.. code-block:: python

    git clone https://github.com/bidfx/bidfx-api-py.git


Installation
------------

The library is setup to use the ``pip`` package manager.
It can be installed running ``pip`` as follows.

.. code-block:: sh

    pip install bidfx-api


Session configuration
=====================

The ``bidfx`` package contains all of the classes,
methods and event handlers that are necessary to subscribe to pricing from
multiple pricing services.

To work with the API, the first thing you need to do is create a ``Session``.
`Session` is the core class that allows you to subscribe to prices and trade via BidFX.
To connect to the BidFX platform the Session must first be configured.
There are three ways to configure the Session:

1. by using a default config file located in your home directory
2. specifying a named config file from any location
3. creating a config in code.

Details of how to configure the API can be found at `configuration`.
In our examples we will just use the default method to create and configure a Session as follows.

.. code-block:: python

    from bidfx import Session
    session = Session.create_from_ini_file()


Pricing API
===========

The Pricing API interface is obtained as a property of the `Session`.
Pricing makes use of a publish-subscribe paradigm in which clients
register for price updates by subscribing on subjects. A `Subject` identifies
a view of an individual instruments for which realtime pricing may be obtained.

LPs publish streams of realtime prices against large numbers of subjects.
The BidFX price service matches the client's subscribed subjects against the total universe of
published subjects and forwards on to each client only those price updates
that match their subscriptions.

Pricing uses threads to manage asynchronous communication with the price servers.
The threads need to be started explicitly.
Realtime data is passed back to the user-code via event-handling callback functions.
The normal pattern for using the pricing API is:

1. configure the Session
2. fetch the pricing API from the Session
3. register the pricing callback functions
4. start the pricing threads
5. subscribe to Subjects


Minimal example
---------------

Here is a small but complete example of a price consuming application:


.. code-block:: python

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


    if __name__ == "__main__":
        main()


After subscribing to a Subject, you will start receiving related `PriceEvent`
notifications via the registered callback function: ``pricing.callbacks.price_event_fn``.

In addition, if required, whenever the status of a subscription changes a `SubscriptionEvent` notification is published via the
registered subscription status callback ``pricing.callbacks.subscription_event_fn``.


FX streaming example
--------------------

Example of streaming (RFS) firm spot rates direct from LPs

.. code-block:: python

    import logging

    from bidfx import Session, Subject


    def on_price_event(event):
        if event.price:
            print(
                "{} {} {} {} {} -> {}".format(
                    event.subject[Subject.CURRENCY_PAIR],
                    event.subject[Subject.LIQUIDITY_PROVIDER],
                    event.subject[Subject.DEAL_TYPE],
                    event.subject[Subject.CURRENCY],
                    event.subject[Subject.QUANTITY],
                    event.price,
                )
            )


    def on_subscription_event(event):
        print(f"Subscription to {event}")


    def on_provider_event(event):
        print(f"Provider {event}")


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
        pricing.start()

        pricing.subscribe(
            pricing.build.fx.stream.spot.liquidity_provider("DBFX")
            .currency_pair("EURUSD")
            .currency("EUR")
            .quantity(1000000)
            .create_subject()
        )
        pricing.subscribe(
            pricing.build.fx.stream.spot.liquidity_provider("DBFX")
            .currency_pair("USDJPY")
            .currency("USD")
            .quantity(5000000)
            .create_subject()
        )


    if __name__ == "__main__":
        main()



Building subjects
-----------------

Because BidFX connects to many different liquidity providers our instrument symbology is necessarily complex. 
Each instrument that can be subscribed on is defined by a unique `Subject`.
A Subject is an immutable object that looks and behaves similar to a read-only `dict`.
It contains many key-value string pairs called *Subject components*.
FX price Subjects can be particularly large,
especially when it comes to swaps and NDS which are described by many components.
Here are a few example Subjects parsed from strings (not recommended):

.. code-block:: python

    from bidfx import Subject
    indi_spot = Subject.parse_string("AssetClass=Fx,Exchange=OTC,Level=1,Source=Indi,Symbol=USDCAD")
    rfs_spot  = Subject.parse_string("AssetClass=Fx,BuySideAccount=GIVE_UP_ACCT,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=CSFX,Quantity=5000000.00,RequestFor=Stream,Symbol=EURUSD,Tenor=Spot,User=smartcorp_api")
    rfq_ndf   = Subject.parse_string("AssetClass=Fx,BuySideAccount=GIVE_UP_ACCT,Currency=USD,DealType=NDF,Level=1,LiquidityProvider=DBFX,Quantity=1000000.00,RequestFor=Quote,Symbol=USDKRW,Tenor=1M,User=smartcorp_api")

Subjects are case sensitive. Their components are ordered alphabetically by key.
It is important to get the Subject syntax and component spellings right,
otherwise the subscription will fail.
This is non-trivial for newcomers as Subject formats vary by both asset class and deal type.

To build Subjects correctly, its is best to use a *Subject builder* which provides
method-chaining to aid syntax discovery and validation to check the result.
The API provides a Subject builder as a property of the `PricingAPI` interface.
This allows you to construct to the following types of Subject:

- Indicative FX
- FX Request for Stream (RFS/ESP) - Spot, Forward, NDF
- FX Request for Quote (RFQ) - Spot, Forward, NDF, Swap and NDS
- Future
- Equity

Below are some Subject building examples that produce the same Subjects as the parsed strings above.

.. code-block:: python

    from bidfx import Session
    pricing = Session.create_from_ini_file().pricing
    indi_spot = pricing.build.fx.indicative.spot.currency_pair("USDCAD").create_subject()

    rfs_spot  = pricing.build.fx.stream.spot.liquidity_provider("CSFX").currency_pair(
        "EURUSD").currency("EUR").quantity(5000000).create_subject()

    rfq_ndf   = pricing.build.fx.stream.spot.liquidity_provider("DBFX").currency_pair(
        "USDKRW").currency("USD").quantity(1000000).create_subject()

    # To subscribing to pricing
    pricing.subscribe(indicative_spot)
    
    # To un-subscribing from pricing
    pricing.unsubscribe(indicative_spot)


Trading API
===========

TODO when stable.

