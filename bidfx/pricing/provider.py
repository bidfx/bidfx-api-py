__all__ = ["PriceProvider"]

import abc

from .subject import Subject


class PriceProvider(abc.ABC):
    """
    A PriceProvider is an interface that encapsulates the operations of an underlying price provider implementation.
    """

    @abc.abstractmethod
    def start(self):
        """
        Starts the pricing threads which connect to and manage real-time price services asynchronously.
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """
        Stops the pricing threads.
        """
        pass

    @abc.abstractmethod
    def subscribe(self, subject):
        """
        Subscribes to real-time price publications on a given `Subject` representing an instrument.

        :param subject: The price subject to subscribe to.
        :type subject: Subject
        """
        pass

    @abc.abstractmethod
    def unsubscribe(self, subject):
        """
        Un-subscribes from a previously subscribed price `Subject`.

        :param subject: The price subject to unsubscribe from.
        :type subject: Subject
        """
        pass
