__all__ = ["Callbacks"]


def _noop(_event):
    pass


class Callbacks:
    """
    This class provides a set of callback functions that can be overridden by the API user
    to handle the different types of event that are published by the Pricing API.
    """

    __slots__ = (
        "price_event_fn",
        "subscription_event_fn",
        "provider_event_fn",
    )

    def __init__(self):
        self.price_event_fn = _noop
        """
        The callback function to be used for handling price events.

        :type: def function(event: `PriceEvent`)
        """
        self.subscription_event_fn = _noop
        """
        The callback function to be used for handling subscription events.

        :type: def function(event: `SubscriptionEvent`)
        """
        self.provider_event_fn = _noop
        """
        The callback function to be used for handling provider events.

        :type: def function(event: `ProviderEvent`)
        """
