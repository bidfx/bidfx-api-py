__all__ = ["BIDFX_API_INFO"]

import uuid


class _BidFxAPI:
    """
    This class provides the identifying information for the BidFX Python API including its version.
    """

    def __init__(self, version="1.1.4"):
        self._name = "bidfx-public-api-py"
        self._product = "BidFXPython"
        self._version = version
        self._guid = uuid.uuid4().hex

    @property
    def name(self):
        """
        Gets the name of the API.
        """
        return self._name

    @property
    def product(self):
        """
        Gets the product of the API.
        """
        return self._product

    @property
    def version(self):
        return self._version

    @property
    def guid(self):
        return self._guid


BIDFX_API_INFO = _BidFxAPI()
