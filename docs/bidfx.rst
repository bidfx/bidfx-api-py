*************
BidFX package
*************

.. module:: bidfx

The BidFX API provides a *Session* via which access is given to all of the API features.
The Session represents a applications's working session with the API for accessing
either real-time pricing or the trading capabilities.
Sessions open and maintain network connections to services running within the BidFX platform.
They create threads to manage these connections asynchronously.
These threads must be started explicitly after the Session has been configured.

**Typical Usage**

.. code-block:: python

    # Create the Session from the INI file at .bidfx/api/config.ini
    session = Session.create_from_ini_file()

    # Set the callback for receiving price update events
    session.pricing.callbacks.price_event_fn = on_price_event

    # Set the pricing threads
    session.pricing.start()

    # Subscribe to streaming FX prices for €1m EURUSD at spot from DBFX
    subject = session.pricing.build.fx.stream.spot.liquidity_provider("DBFX")
        .currency_pair("EURUSD").currency("EUR").quantity(1000000).create_subject()
    session.pricing.subscribe(subject)



Session
=======

.. autoclass:: Session
    :members:


BidFXError
==========

.. autoexception:: BidFXError
    :members:


PricingError
============

.. autoexception:: PricingError
    :members:


InvalidSubjectError
===================

.. autoexception:: InvalidSubjectError
    :members:




