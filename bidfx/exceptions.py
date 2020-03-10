__all__ = [
    "BidFXError",
    "PricingError",
    "InvalidSubjectError",
    "IncompatibleVersionError",
]


class BidFXError(Exception):
    """
    Base class for all errors raised by the BidFX API. Extends `Exception`.
    """

    pass


class PricingError(BidFXError):
    """
    Base class for all errors raised by the BidFX Pricing API. Extends `BidFXError`.
    """

    pass


class InvalidSubjectError(PricingError):
    """
    Error indicating the a price `Subject` is invalid. Extends `PricingError`.
    """

    pass


class IncompatibleVersionError(PricingError):
    """
    Error indicating a protocol version incompatibility between client and server. Extends `PricingError`.
    """

    pass
