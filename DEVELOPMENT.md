![BidFX logo](docs/_static/bidfx_logo_128.png)

# Development Notes


## Bitbucket

During development of the library the source code has been kept in 
[Bitbucket](http://git.dev.tradingscreen.com:7990/projects/BIDFX/repos/public-api-python/browse). 
Download the API source with the command:

```sh
git clone https://git.dev.tradingscreen.com:7990/scm/bidfx/public-api-python
```

## Github

As part of the BidFX Open Source initiative, we intend to published the source code on the
[BidFX Github Page](https://github.com/bidfx).
When available, you will be able to get the API with the command:

```sh
git clone https://github.com/bidfx/bidfx-api-python.git
```

## IDE

For Python development we recommend [PyCharm](https://www.jetbrains.com/pycharm/) from JetBrains.


## PIP installation

The library is setup to use the `pip` package manager.
Pip will install all of the the API dependencies.
The API relies only on Python3 built-ins and a few select libraries.
You can see a list of dependencies in the [requirements.txt](requirements.txt).
Developers can install the requirements, without installing the BidFX library, 
by issuing the command.

```sh
pip install -r requirements.txt
```

Those who prefer to install from the source distribution can do so with `pip` 
by running the following command.

```sh
pip install .
```

## Running tests

Unit tests are provided in the [tests](tests) directory.
Test the package by running the unit tests.
Issue issue the command below from the top-level directory or run from an IDE.

```sh
python -m unittest
```

## Example programs

Plenty of example programs demonstrating the use of the API
are provided in the [examples](examples) directory.
These are split into:

* [Pricing examples](examples/pricing)
* [Trading examples](examples/trading)

It is recommended that all example programs are run successfully before making a new release.


## Certification scripts

In addition to the example programs provided for API users, the source distribution
provides a set of certification test programs.
These were provided to satisfy that the API meets the published BidFX API requirements.
You can find conformance test scripts in the [certification](certification) directory.
These programs are configured and run in the same was as the API examples.

It is recommended that all certification programs are run successfully 
before making a new release.


## Making a distribution

The distribution is created by running the `make`. Run the command:

```sh
make dist
```

To build a new distribution into a tar file.
The distribution is written to the [dist](dist) directory.

 ```sh
$ ls dist
bidfx-api-python-0.1.0.tar.gz
bidfx_api_python-0.1.0-py3-none-any.whl
```

## API documentation

Making a distribution will also build the documentation from the docstrings in the Python source code.
You can build the docs and test them in a browser by running:

 ```sh
make docs
```

The docs are generated as HTML with the top-level page at `docs/build/html/index.html`.


## Version number

The library version is defined in the file [bidfx/_version.py](bidfx/_version.py).
The version number must be increased for each new release.
