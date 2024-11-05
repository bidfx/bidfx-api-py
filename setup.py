import sys

import setuptools

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python versions less that 3.6 are not supported")

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = "1.1.4"

setuptools.setup(
    name="bidfx-api",
    version=version,
    author="Paul Sweeny",
    author_email="paul.sweeny@bidfx.com",
    description="Public API for accessing the BidFX platform for pricing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bidfx/bidfx-api-py",
    download_url="https://github.com/bidfx/bidfx-api-py/tarball/v" + version,
    packages=setuptools.find_packages(),
    install_requires=requirements,
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Natural Language :: English",
        "Development Status :: 5 - Production/Stable",
    ],
    python_requires=">=3.6",
)
