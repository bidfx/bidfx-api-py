__all__ = [
    "PriceEvent",
    "SubscriptionEvent",
    "ProviderEvent",
    "SubscriptionStatus",
    "ProviderStatus",
]

from enum import Enum, auto, unique

from .subject import Subject


class PriceEvent:
    """
    This class defines a Price Event that gets published for each price tick received on a subscription.
    Price events should be handled by setting a callback function via `PricingAPI.callbacks`.
    The callback function could be implemented and used as follows.

    .. code-block:: python

        def on_price_event(event):
            if event.price:
                print("price update {} {} / {})".format(
                    event.subject[Subject.CURRENCY_PAIR],
                    event.price.get(Field.BID, ""),
                    event.price.get(Field.ASK, "")))

        def main():
            session = Session.create_from_ini_file()
            session.pricing.callbacks.price_event_fn = on_price_event

    Notice from above that you can use the constants provided by:
     * `Subject` to access the components of the subject
     * `Field` to access the fields of the price update.

    """

    __slots__ = ("subject", "price", "full")

    def __init__(self, subject, price, full):
        """
        :param subject: The unique subject of the price subscription.
        :type subject: Subject
        :param price: The price as a map for fields.
        :type price: dict
        :param full: Flag indicating if this is a full or partial price update.
        :type full: bool
        """

        self.subject = subject
        """
        The `Subject` of the price event.

        :type: Subject
        """
        self.price = price
        """
        The map of updated price field. 

        :type: dict
        """
        self.full = full
        """
        A boolean flag indicating if the update represents a full or partial update.
        The value is set to `True` for a full price image and `False` for a partial update. 

        :type: bool
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.subject!r}, Price({self.price!r}) Full({self.full!r}))"

    def __str__(self) -> str:
        update = "Full" if self.full else "Partial"
        return f"{self.__class__.__name__} {self.subject} is {self.price} {update}"


@unique
class SubscriptionStatus(Enum):
    """
    This enum defines the number of different statuses that can be applied to a pricing subscription.
    """

    OK = auto()
    """The subscription is OK. This state is not normally published, it is implied by any price update."""
    PENDING = auto()
    """The subscription is pending an update from an upstream service or provider."""
    STALE = auto()
    """The subscription is stale, possibly due to a connection issue."""
    CANCELLED = auto()
    """The subscription has been cancelled."""
    DISCONTINUED = auto()
    """The subscription has been discontinued by the provider (common on RFQ subscriptions)."""
    PROHIBITED = auto()
    """The subscription is prohibited by entitlements."""
    UNAVAILABLE = auto()
    """The subscription is unavailable perhaps due to routing issues or setup."""
    REJECTED = auto()
    """The subscription has been rejected by the provider."""
    TIMEOUT = auto()
    """The subscription has timed out."""
    INACTIVE = auto()
    """The subscription has been detected as being inactive."""
    EXHAUSTED = auto()
    """The subscription is has exhausted a usage limit or resource."""
    CLOSED = auto()
    """The subscription has been closed (normally by the client API). This is a terminal state."""


class SubscriptionEvent:
    """
    This class defines a Subscription Event that gets published whenever the status of subscription changes.
    Subscription events should be handled by setting a callback function via `PricingAPI.callbacks`.
    The callback function could be implemented and used as follows.

    .. code-block:: python

        def on_subscription_event(event):
            print(f"Subscription to {event.subject} is {event.status.name}")

        def main():
            session = Session.create_from_ini_file()
            pricing.callbacks.subscription_event_fn = on_subscription_event
    """

    __slots__ = ("subject", "status", "explanation")

    def __init__(self, subject, status, explanation):
        """
        :param subject: The unique subject of the price subscription.
        :type subject: Subject
        :param status: The subscription status.
        :type status: SubscriptionStatus
        :param explanation: An explanation of the status reason.
        :type explanation: str
        """

        self.subject = subject
        """
        The `Subject` of the price event.

        :type: Subject
        """
        self.status = status
        """
        The `SubscriptionStatus` associated with the event.

        :type: SubscriptionStatus
        """
        self.explanation = explanation
        """
        An optional explanation message for the status event.

        :type: str
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.subject!r}, {self.status!r}, {self.explanation!r})"

    def __str__(self) -> str:
        if self.explanation:
            return f"{self.__class__.__name__} {self.subject} is {self.status.name}: {self.explanation}"
        return f"{self.__class__.__name__} {self.subject} is {self.status.name}"


@unique
class ProviderStatus(Enum):
    """
    This enum defines the number of different statuses that can be applied to a price provider.
    """

    READY = auto()
    """The price provider is ready for use."""
    DISABLED = auto()
    """The price provider is has been disabled."""
    DOWN = auto()
    """The price provider is down and attempting to reconnect."""
    UNAVAILABLE = auto()
    """The price provider is unavailable."""
    INVALID = auto()
    """The price provider is invalid most likely due to misconfiguration."""
    CLOSED = auto()
    """The price provider has been closed. This is the terminal state."""


class ProviderEvent:
    """
    This class defines Provider Event that gets published whenever the status of price provider changes.
    Provider events should be handled by setting a callback function via `PricingAPI.callbacks`.
    The callback function could be implemented and used as follows.

    .. code-block:: python

        def on_provider_event(event):
            print(f"Provider {event.provider} is {event.status.name}")

        def main():
            session = Session.create_from_ini_file()
            pricing.callbacks.provider_event_fn = on_provider_event
    """

    __slots__ = ("provider", "status", "explanation")

    def __init__(self, provider, status, explanation):
        """
        :param provider: The unique name of the price provider.
        :type provider: str
        :param status: The provider status.
        :type status: ProviderStatus
        :param explanation: An explanation of the status reason.
        :type explanation: str
        """
        self.provider = provider
        """
        The name of the price provider that issued the event.

        :type: str
        """
        self.status = status
        """
        The `ProviderStatus` associated with of the event.

        :type: ProviderStatus
        """
        self.explanation = explanation
        """
        An optional explanation message for the status event.

        :type: str
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.provider!r}, {self.status!r}, {self.explanation!r})"

    def __str__(self) -> str:
        if self.explanation:
            return f"{self.__class__.__name__} {self.provider} is {self.status.name}: {self.explanation}"
        return f"{self.__class__.__name__} {self.provider} is {self.status.name}"
