***********
About BidFX
***********

BidFX is the market-leading provider of electronic trading solutions for the global foreign exchange marketplace. 
BidFX has addressed the challenges of the FX market by introducing a complete suite of negotiation protocols
– which include: auto-routing, streaming, request-for-quote, voice,
algo-trading and best execution – via a cloud-based SaaS trading platform.
BidFX offer clients access to a cutting edge, broker-neutral,
Execution Management System (EMS) backed by a hub to all major bank's
algo suites. You can read about all BidFX products on the main
`BidFX Website <https://www.bidfx.com>`_.


BidFX APIs
==========

BidFX clients access the trading platform via a dedicated User Interface (UI)
either on their desktop PC, web browser or mobile device.

Public APIs provide a secondary means of accessing the trading platform that can either supplement
the UI or replace it entirely in some use cases, including: systematic trading, OMS integration and market intelligence.
BidFX place significant emphasis on API support and therefore
provide a suite of APIs for different high-level programming languages and common protocols.

You can read about the complete BidFX API range, and their different capabilities, at
`BidFX API Overview <https://www.bidfx.com/apis>`_.


Python API
==========

This document describes the *BidFX Public API for Python*.
The Python API is written pure Python and is compatible with ``Python 3.6`` and above.
All of the code examples below are presented in Python.

We use the nomenclature *Public* to indicated that
this API is designed and maintained for public use by BidFX clients.
Being Public implies a degree of support, API stability and future
compatibility appropriate to client usage.


Source of liquidity
-------------------

BidFX are connected to all the major tier-1 banks and FX liquidity providers (LP).
LPs publish tradable FX price/quotes into the BidFX platform using the FIX protocol.
The quotes from LPs are firm prices with an associated *price-ID* that needs
to be attached to any order placed against the quote.
The BidFX platform consumes billions for FIX messages per day.
We provision high-bandwidth, cross-connect circuits in the main global data centres for this purpose.
BidFX connect to banks where they host their price engines, in particular in:

- London (LD4),
- New York (NY4) and
- Tokyo (TY3).


Last look
---------

FX quotes are short-lived and LPs reserve the right of **last look**.
A quote usually is good for no more than a few hundred milliseconds.
Network latency between the client application and the LP is therefore
a significant consideration if we want to avoid order rejections.

If clients intend to trade directly against price-IDs, then it is recommended
that they run their application very close to the source of liquidity
and cross-connect within the same data centre.
Alternatively, clients may route their orders to the BidFX *Strategy Server*
which is located close to LPs to minimise both rejections and slippage.


Binary protocols
----------------

The BidFX Python API implements a bespoke binary protocols that are optimised
to deliver realtime quotes from LPs directly to into a client's application with minimal latency.
The binary delivery mechanism is more efficient, by orders of magnitude, than the FIX protocol.
Furthermore, using the *publish and subscribe* paradigm, BidFX servers
publish only those quotes that are subscribed to, thus saving significantly in network traffic.
