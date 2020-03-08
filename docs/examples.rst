****************
Example Programs
****************

The BidFX API comes bundled with a number of example programs to demonstrate its usage.
These can be found under the ``examples`` directory, immediately under the top-level directory.
Two sets of examples are provided to demonstrate the:

* Pricing API
* Trading API

These are located in separate sub-directories called ``examples/pricing`` and ``examples/trading``.


Configuration
=============

All of the examples share a common means of configuration using a Window-style INI file.
Out of the box the examples will attempt to locate the API configuration in the file
``.bidfx/api/config.ini`` located in the users home directory i.e. ``$HOME/.bidfx/api/config.ini``.
An example config file is provided at ``examples/config_example.ini`` to get you started.
Tailor the configuration as follows before attempting to run the examples.

.. code-block:: sh

    cp examples/config_example.ini $HOME/.bidfx/api/config.ini
    vi $HOME/.bidfx/api/config.ini
    chmod 600 $HOME/.bidfx/api/config.ini

Edit the INI file to add the host name and user credentials provided by your BidFX account manager.
It is best to make the file read-only to protect the credentials.
See `configuration` for documentation of the supported parameters.


Running the examples
====================

Running in an IDE
-----------------

For running the example programs and for general Python development, 
we recommend an integrated development environment (IDE) designed for programming in Python. 
We like the `PyCharm <https://www.jetbrains.com/pycharm/>`_ from JetBrains.
With **PyCharm** the examples can be run directly by
right-clicking on the example program in the ``Project`` tab and selecting ``Run``.


Running from the command line
-----------------------------

You may also run the examples directly from the command line.
The examples are all executable Python scripts.

The scripts will select the first version of ``python`` from your ``$PATH`` environment variable.
The scripts can be run directly on UNIX as follows.

.. code-block:: sh

    ./examples/pricing/example_indicative_fx.py

Alternatively, if you want to use a specific version of ``python`` then pass the example program 
file as the argument to the version of ``python`` that you prefer.
