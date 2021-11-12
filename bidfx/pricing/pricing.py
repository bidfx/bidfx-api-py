__all__ = ["PricingAPI"]

import logging

from ._pixie.pixie_provider import PixieProvider
from ._puffin.puffin_provider import PuffinProvider
from ._subject_builder import SubjectBuilder
from .callbacks import Callbacks
from .provider import PriceProvider
from .subject import Subject
from ..exceptions import PricingError

log = logging.getLogger("bidfx.pricing")

PUFFIN_PROTOCOL = "Puffin"
"""
The Pixie protocol. A binary publish and subscribe protocol designed for efficient transmission 
of shared price streams such as exchange listed pricing.
"""

PIXIE_PROTOCOL = "Pixie"
"""
The Pixie protocol. A binary publish and subscribe protocol designed for efficient transmission 
of exclusive tradable price streams and RFQ.
"""


class DisabledProvider(PriceProvider):
    """
    A disabled price provider that does nothing. Provides a way to turn off one of the protocols by config.
    """

    def start(self):
        pass

    def stop(self):
        pass

    def subscribe(self, subject):
        pass

    def unsubscribe(self, subject):
        pass


class PricingAPI(PriceProvider):
    """
    Pricing is the top-level API interface for accessing the real-time pricing services of BidFX.
    It implements two `PriceProvider` implementations:
    one for *exclusive pricing* that uses the Pixie protocol,
    and one for *shared pricing* that uses the Puffin protocol.
    """

    def __init__(self, config_parser):
        """
        :param config_parser: The API configuration.
        :type config_parser: configparser.ConfigParser
        """
        config_section = config_parser["Exclusive Pricing"]
        self._callbacks = Callbacks()
        self._subject_builder = SubjectBuilder(
            config_section["username"], config_section["default_account"]
        )
        self._pixie_provider = self._create_provider(
            config_parser, "Exclusive Pricing", PIXIE_PROTOCOL
        )
        self._puffin_provider = self._create_provider(
            config_parser, "Shared Pricing", PUFFIN_PROTOCOL
        )

    def _create_provider(self, config_parser, section, protocol):
        config_section = config_parser[section]
        if config_section.getboolean("disable", False):
            log.info(
                f"{section} provider ({protocol} protocol) has been disabled by config"
            )
            return DisabledProvider()
        return PricingAPI.create_price_provider(
            config_section, self.callbacks, protocol
        )

    def start(self):
        self._pixie_provider.start()
        self._puffin_provider.start()

    def stop(self):
        self._pixie_provider.stop()
        self._puffin_provider.stop()

    def subscribe(self, subject):
        if self._is_exclusive_subject(subject):
            self._pixie_provider.subscribe(subject)
        else:
            self._puffin_provider.subscribe(subject)
        log.debug("successfully subscribed to: " + str(subject))

    def unsubscribe(self, subject):
        if self._is_exclusive_subject(subject):
            self._pixie_provider.unsubscribe(subject)
        else:
            self._puffin_provider.unsubscribe(subject)
        log.info("unsubscribe from: " + str(subject))

    @property
    def build(self):
        """
        Provides a handle to a the subject builder interface that provides a convenient way to construct a
        well-formed and validated price `Subject` by using a blend of method-chaining and the builder pattern.
        The method-chains guide the user to find a correct subject for common classes of instrument,
        and the builder then validates the resulting subject. For example:

        .. code-block:: python

            # Create an indicative FX spot subject
            pricing.build.fx.indicative.spot.currency_pair("GBPAUD").create_subject()

            # Create a tradable FX OTC spot subject
            pricing.build.fx.stream.spot.liquidity_provider("DBFX").currency_pair("USDJPY").currency("USD").quantity(5000000).create_subject()

        :return: A method-chain that should lead to the creation a valid `Subject`.
        """
        return self._subject_builder

    @property
    def callbacks(self):
        """
        Accessor for setting callbacks for pricing related events.

        :return: The set of `Callbacks` that determine which user-functions get called for each type of event.
        :rtype: Callbacks
        """
        return self._callbacks

    @staticmethod
    def _is_exclusive_subject(subject):
        return Subject.USER in subject and subject[Subject.ASSET_CLASS] == "Fx"

    @staticmethod
    def create_price_provider(config_section, callbacks, protocol):
        """
        Creates a price provider for a given protocol. Allowed values are 'Pixie' or 'Puffin'.
        Most applications will not use this method directly as the `PricingAPI` will create
        the required price providers.

        :param config_section: Provider section of the API configuration.
        :type config_section: configparser.ConfigParser[section]
        :param callbacks: The callback functions to handle events.
        :type callbacks: Callbacks
        :param protocol: The protocol implementation for the provider. Defaults to 'Pixie'.
        :type protocol: str
        :return: A new price provider instance.
        :rtype: PriceProvider
        :raises PricingError: if the protocol is not supported.
        """
        if protocol == PIXIE_PROTOCOL:
            return PixieProvider(config_section, callbacks)
        if protocol == PUFFIN_PROTOCOL:
            return PuffinProvider(config_section, callbacks)
        raise PricingError(f"unsupported pricing protocol: {protocol}")
