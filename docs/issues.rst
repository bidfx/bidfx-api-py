****************
Potential issues
****************


On-boarding issues
==================

Credentials
-----------

Applications need valid credentials to connect to services using the BidFX API.
Please don't use personal credentials for programmatic access via the API.
BidFX on-boarding staff provide dedicated credentials for API usage.
Credentials will differ between UAT and Production, so be sure not to mix the two.

If you create a ``Session`` using an incorrect username or password,
or you fail to configure credentials, then the API will issue a suitable error soon after starting.


API product
-----------

A valid credentials are insufficient by themselves to access resources using the API.
The user also requires a backend *product assignment* for API access.
Your BidFX account manager will set this up for you.
There may be a usage charge associated with API access.


Booking account
---------------

FX subscriptions require a booking account. 
Prices, session routing and entitlements can differ from one account to another.
If required, a separate account can be set for each subscription
but commonly a single default account is used for all API subscriptions.
The *default account* is configured on the API ``Session`` config.
Please verify with your account manager to ensure you are providing the correct account to the API.


Relationships and entitlements
------------------------------

You might find that you can connect to the price service, 
receive some pricing but not get data for all subscriptions;
perhaps some LPs or currency pairs are absent. 
This situation is most likely due to the assigned customer relationships or entitlements for the user account. 
Talk to you account manager to ensure that all of your LPs have been fully on-boarded.


Connectivity issues
===================

First time users of the API may experience connectivity issues due to firewalls, 
content filtering or network accelerator devices managed by their corporate network team.


Firewalls
---------

A firewall is in place at most organisations to provide basic network security.
It is often necessary for API users to request their local network team to
white-list an IP address or open a port in the firewall to the required BidFX POP.
See `POPs` for a list of IP addresses.

If you encounter network issues then it is possible to test the connectivity to BidFX using the
``ping`` and ``telnet`` commands as follows:

.. code-block:: sh

    $ ping ln-tunnel.uatprod.tradingscreen.com
    PING ln-tunnel.uatprod.tradingscreen.com (199.27.86.91): 56 data bytes
    64 bytes from 199.27.86.91: icmp_seq=0 ttl=58 time=1.175 ms
    64 bytes from 199.27.86.91: icmp_seq=1 ttl=58 time=1.076 ms

    $ telnet ln-tunnel.uatprod.tradingscreen.com 443
    Trying 199.27.86.91...
    Connected to ln-tunnel.uatprod.tradingscreen.com.
    Escape character is '^]'.

Consult your network team if either command returns an error or hangs.


Network devices
---------------

Security-conscious organisations deploy sophisticated network devices to inspect packets,
shape traffic and optimise bandwidth.
Such devices can corrupt the message flow to BidFX and cause a protocol marshalling error, 
quickly followed by a session disconnect.

Network security devices may allow the initial connection through to BidFX but
interfere subsequently with either the price protocol or the TLS security layer.
Packet inspection might, for example, appear to the API as a man-in-the-middle attack.
Some packet inspection devices prevent WebSocket upgrades by filtering HTTP headers,
either intentionally or unintentionally.

The observed symptom in these cases is a read timeout or an SSL handshake error,
received soon after establishing the connection.
The solution to all of these issues is to request your company's network team
to bypass the offending device(s) for the BidFX IP addresses and ports.
See `POPs` for a list of IP addresses and ports used by BidFX.


Subscription limits
===================

The BidFX Price Service limits the number of simultaneous price subscriptions that an API may make. 
We restrict subscriptions, both to protect the Price Service from excessive use and to guarantee
a high quality of service for all users. 
The default subscription limits allow hundreds of price subscriptions and are sufficient 
and appropriate for most applications.


Increasing limits
-----------------

BidFX may provide a licence key that grants a larger subscription limit for demanding applications.
The licence key is provided to the API via the ``Session`` config.
To qualify for a higher subscription limit, the client will need to:

- have sufficient CPU capacity to consume the increased price update load,
- run their application physically close to the source of liquidity,
- have a good quality, high bandwidth network connection (ideally a data centre cross-connect to BidFX).

There may be an additional service charge for an increased subscription limit.
Ask your BidFX sales representative for price details.


Latency
=======

FX pricing has the potential to update very rapidly, especially around times of major news announcements.
Too many price subscriptions can generate substantial amounts of network traffic,
causing bandwidth saturation and heavy CPU load on the application host.
If an overworked application becomes a *slow consumer* then it will experience latency.

We recommend all API users to close subscriptions that are no longer required to minimise network load.

If you experience latency then there are a few remedial actions you can take:

- Reduce the number of open subscriptions.
- Change the configuration to increase the price publication throttle.
- Move your application close to your main source of liquidity.
- Install a dedicated network link with high capacity and QoS.
- Ideally cross-connect at the same data center as BidFX.
