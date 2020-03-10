************
FX liquidity
************

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
=========

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
================

The BidFX Python API implements two binary protocols that are optimised
to deliver realtime quotes from LPs directly to into a client's application with minimal latency.
The binary delivery mechanism is more efficient than the FIX protocol used by most banks to publish prices.
Furthermore, using the *publish and subscribe* paradigm, BidFX servers
publish only those quotes that are subscribed to, thus saving significantly in network traffic.
