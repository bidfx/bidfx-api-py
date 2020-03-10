
***************************
BidFX Public API for Python
***************************

The BidFX Python API is a price and trading API that connects to
the BidFX trading platform to subscribe to realtime pricing and to register or submit orders.
The API supports the following features:

 - FX streaming executable prices (RFS)
 - FX request for quote (RFQ)
 - FX and Futures trading with `REST <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ or `WebSockets <https://en.wikipedia.org/wiki/WebSocket>`_.


Most users of the API will trade against the firm quotes received via the Pricing API.
Trading is achieved by using direct API calls which are implemented under the covers by the BidFX WebSocket API.

Contents
========

.. toctree::
   :maxdepth: 2

   about
   user_guide
   examples
   configuration
   POPs
   issues


API docs
========

.. toctree::
   :maxdepth: 1

   bidfx
   pricing


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
