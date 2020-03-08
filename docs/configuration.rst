*****************
API Configuration
*****************

The API is best configured using a Window's style INI file.
It is common to configure the API by supplying the name of the INI on a call `Session.create_from_ini_file()`.
If no filename is provided then the `Session` will look for a file called
``.bidfx/api/config.ini`` in the user's home directory.


Configuration methods
=====================

There are three ways to provide a configuration for the API:

1. by using a default config file located in your home directory
2. specifying a named config file from any location
3. creating a config in code.


Default configuration
---------------------

For convenience, all of configuration items may be provided through a single configuration object.
The API uses a `ConfigParser <https://docs.python.org/3/library/configparser.html>`_
to read its configuration from a Windows-style INI file.

The config file is commonly located at ``$HOME/.bidfx/api/config.ini``.
When using the default INI file location, the `Session` can be created and configured as follows.

.. code-block:: python

    from bidfx import Session
    session = Session.create_from_ini_file()


Non-standard configuration file
-------------------------------

The config file location may be changed by passing a in file name to `Session.create_from_ini_file()`.

.. code-block:: python

    from bidfx import Session
    session = Session.create_from_ini_file("./my_config.ini")


Configuration in code
---------------------

The ``ConfigParser`` can be built directly in code if preferred,
then passed into the `Session` constructor as follows.

.. code-block:: python

    from bidfx import Session
    from configparser import ConfigParser
    config_parser = ConfigParser()
    # configure config manually
    session = Session(config_parser)




INI file sections
=================

There is four sections in the configuration INI file:

- ``[DEFAULT]`` - defines shared properties such as *host* and *port*.
- ``[Exclusive Pricing]`` - is for overrides and properties particular to *Exclusive Pricing* (Pixie protocol).
- ``[Shared Pricing]`` - is for overrides and properties particular to *Shared Pricing* (Puffin protocol).
- ``[Trading]`` - is for overrides and properties particular to the *Trading* features.


Default section
---------------

The ``[DEFAULT]`` section provides default properties that are shared by the other sections.
At present all four protocols can be accessed by tunnelling via a single host on secure port 443.
The required user credentials are also the same for all usages of the API.
These data can therefore be defined once in the ``[DEFAULT]`` section of the configuration.
Should this situation change then it is possible to override default settings in the each specific sections.


Shared pricing section
----------------------

Shared Pricing, as the name suggests, is pricing which is shared between many users.
An example of shared pricing is Exchange Listed Futures;
all exchange members receive the same shared price stream.
The BixFX API currently implements the Puffin protocol for subscribing to shared pricing via a Puffin server.

The configuration of the Price Provider for *shared pricing* requires the following properties:

- host
- port
- username
- password


Exclusive pricing section
-------------------------

Exclusive pricing by contrast is not shared across users.
It is exclusive to one particular user or group of users.
Tradable FX OTC prices direct from liquidity providers are exclusive to the subscribing user.
The BixFX API currently implements the Pixie protocol
for subscribing to exclusive pricing from BidFX price servers.

The configuration of the Price Provider for *exclusive pricing* uses the following properties:

- host
- port
- username
- password
- product_serial
- default_account
- min_interval


Trading section
---------------

Trading functionality is provided by the API using both REST and WebSocket protocols.
Both delivery mechanisms transmit their data using JSON.
The configuration of the trading API requires the following properties:

- host
- port
- username
- password


Example INI config file
=======================

.. code-block:: ini

    [DEFAULT]
    # The host and port number of the BidFX service to connect to.
    host = ny-tunnel.uatprod.tradingscreen.com
    port = 443

    # Provide the API login credentials provided by your BidFX account manager.
    username = smartcorp_api
    password = 4EL77HqPC2W8hQut

    # If you have an API serial key then set it below otherwise leave it blank.
    # product_serial = aad33247deffe2aa2832001f

    [Exclusive Pricing]
    # Use this section to override DEFAULT settings for user-exclusive pricing.

    # When subscribing to user-exclusive quotes, the prices consumed may vary by account.
    # A default account is defined here for use no explicit account has been provided.
    default_account = GIVE_UP_ACCT

    # The minimum price publication interval is given below in milliseconds.
    min_interval = 500

    [Shared Pricing]
    # Use this section to override DEFAULT settings for use with shared pricing.

    [Trading]
    # Use this section to override DEFAULT settings for use when accessing the Trading API.
