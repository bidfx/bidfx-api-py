![BidFX logo](docs/_static/bidfx_logo_128.png)

# Development Notes

## Open Source

The Python API has been open sourced with an Apache 2.0 licence.

### PyPI

The project releases are available on [PyPI](https://pypi.org/project/bidfx-api/) so users can install the
API with the command:

```sh
pip install bidfx-api
```

Instructions for making a release are given below.


### Read The Docs

The project documentation is published online [here](https://docs.bidfx.com/api-py/index.html).


### Github

As part of the BidFX Open Source initiative, we have published the API source code on the
[BidFX Github Page](https://github.com/bidfx).
Users are able to get the API with the command:

```sh
git clone https://github.com/bidfx/bidfx-api-py.git
```


## IDE

For Python development we recommend [PyCharm](https://www.jetbrains.com/pycharm/) from JetBrains.


## PIP installation

The library is setup to use the `pip` package manager.
PIP will install all of the the API dependencies.
The API relies only on Python3 built-ins and a few select libraries.
You can see a list of dependencies in the [requirements.txt](requirements.txt).

Developers can install the requirements, without installing the BidFX library, 
by issuing the command.

```sh
pip install -r requirements.txt
```

To create a release you will also need to install development requirements with the command.

```sh
pip install -r requirements-dev.txt
```

Make will do this for you when you `make release`.


## Testing

### Running unit tests

Unit tests are provided in the [tests](tests) directory.
To test the package by running the unit tests type `make test`.
Alternatively issue the command below from the top-level directory or run from an IDE.

```sh
python -m unittest
```

### Example programs

Plenty of example programs demonstrating the use of the API
are provided in the [examples](examples) directory.
These are split into:

* [Pricing examples](examples/pricing)
* [Trading examples](examples/trading)

It is recommended that all example programs are run successfully before making a new release.


### Certification scripts

In addition to the example programs provided for API users, the source distribution
provides a set of certification test programs.
These were provided to satisfy that the API meets the published BidFX API requirements.
You can find conformance test scripts in the [certification](certification) directory.
These programs are configured and run in the same was as the API examples.

It is recommended that all certification programs are run successfully 
before making a new release.


## Release procedure

### Code formatting

The Python source code is pretty formatted for consistency using [Black](https://github.com/psf/black).
You can trigger a manual reformat by typing `make pretty` which runs `Black` over all source files.
You can also configure your IDE to reformat each Python file as it is saved.


### Version number

The library version is managed by [bump2version](https://github.com/c4urself/bump2version) 
and the version number is defined in the file [setup.cfg](setup.cfg).
A number of source and doc files contain the version number so,  
unless you want to update them all manually, the version number must be increased for each new release 
by running `make version` to bump to the next minor version number.
This just runs:

 ```sh
bumpversion minor
```

### API documentation

Making a distribution will also build the documentation from the docstrings in the Python source code.
The docs are created using [Sphinx](https://github.com/sphinx-doc/sphinx)
You can build the docs and test them in a browser by running:

 ```sh
make docs
```

The docs are generated as HTML with the top-level page at `docs/build/html/index.html`.

### Making a distribution

The distribution is created by running the [setup.py](setup.py) which is done via `make`. 
To create a distribution run the command:

```sh
make dist
```

This will build a new distribution into a tar file.
The distribution is written to the [dist](dist) directory as follows.

 ```sh
$ ls dist
bidfx-api-1.1.0.tar.gz
bidfx_api-1.1.0-py3-none-any.whl
```

### Making a release

The project uses [Twine](https://github.com/pypa/twine) to manage publishing API releases to [PyPI](https://pypi.org).
Trigger a release by typing `make release` or test the process on [Test PyPI](https://test.pypi.org) 
by typing `make test-release`.

To get the release procedure to work you will have to install an API key for both PyPI accounts
in your `$HOME/.pypirc` file.
Instructions are provided when you set up an account on the PyPI web site.
