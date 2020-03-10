__all__ = ["Session"]

from configparser import ConfigParser
from pathlib import Path

from ._bidfx_api import BIDFX_API_INFO
from .pricing.pricing import PricingAPI


class Session:
    """
    A Session is the top-level API class which gives access to all of the features of the API.
    It represents a client’s working session with the API.
    """

    def __init__(self, config_parser):
        """
        :param config_parser: The API configuration settings.
        :type config_parser: configparser.ConfigParser
        """
        self._pricing = PricingAPI(config_parser)

    @staticmethod
    def create_from_ini_file(config_file="~/.bidfx/api/config.ini"):
        """
        Creates a new Session using configuration data parsed from an INI file.
        The default behaviour is to search for the file ``.bidfx/api/config.ini`` in the user's home directory.

        :param config_file: is the name of the INI file.

        :return: the `Session` configured from the configuration file.
        """
        config = ConfigParser()
        path = Path(config_file).expanduser()
        if not config.read(path):
            raise FileNotFoundError(f"could not find config in {path}")
        return Session(config)

    @property
    def pricing(self):
        """
        Gets the Pricing API session used for subscribing to realtime _prices.

        :return: A configured interface to the `PricingAPI`.
        :rtype: PricingAPI
        """
        return self._pricing

    @staticmethod
    def version() -> str:
        """
        Gets the API version number.

        :rtype: str
        """
        return BIDFX_API_INFO.version
