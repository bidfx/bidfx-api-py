__all__ = ["Subject"]

import itertools


class Subject:
    """
    A subject is an immutable, multi-component identifier used to identify instruments
    that may be subscribed to via the pricing API. Subjects are represented as tuples of many nested tuple pairs,
    where each pair provides a component key and value. Subject components are alphabetically ordered by key.

    Example subjects are:

    * ``AssetClass=Fx,BuySideAccount=ABC,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=DBFX,\
    Quantity=100000.00,RequestFor=Stream,Symbol=EURUSD,Tenor=Spot,User=smartcorp_api``

    * ``AssetClass=Fx,Exchange=OTC,Level=1,Source=Indi,Symbol=USDJPY``

    Subject are safe to compare for equality and to use as the keys of a dictionary.
    Subjects can be converted to string using ``str(subject)`` for display purposes.
    Instances of the subject class can be used much like a `dict` to pull out the individual component parts.
    For example:

    >>> subject = Subject(...)
    >>> ccy_pair = subject[Subject.CURRENCY]

    A number of common subject component keys are provided as constants of the Subject class for this purpose.
    """

    def __init__(self, components):
        """
        :param components: A tuple of subject components, key-value pairs as tuples.
        :type components: tuple
        """
        self._components = components

    def flatten(self):
        """
        Flattens the subject into a simple list of the subject's key and value pairings.

        :return: A flattened list of strings.
        :rtype: list
        """
        return list(itertools.chain(*self._components))

    @staticmethod
    def parse_string(s):
        """
        Creates a new Subject by parsing the string form of subject.

        :param s: The string to be parsed.
        :type s: str

        :return: A new Subject
        :rtype: Subject
        """
        return Subject(tuple(map((lambda c: tuple(c.split("="))), s.split(","))))

    @staticmethod
    def from_dict(d):
        """
        Creates a new Subject from a dictionary.

        :param d: The dictionary to convert.
        :type d: dict

        :return: A new Subject
        :rtype: Subject
        """
        return Subject(tuple(sorted(d.items())))

    def get(self, key, default):
        """
        Gets the value of a Subject component.  The component value is returned
        if the component is present in the subject, otherwise the default value is returned.

        :param key: The key of the subject component to get.
        :type key: str

        :param default: The default value to be returned if the key is not present in the subject.
        :type default: str

        :return: A the value of the component mapped from the *key*, or the *default* value.
        :rtype: str
        """
        return self._find(key, (None, default))[1]

    def __getitem__(self, key):
        return self._find(key, (None, None))[1]

    def _find(self, key, default):
        return next((c for c in self._components if c[0] == key), default)

    def __contains__(self, key):
        """Checks if this Subject contains a component with the given key."""
        return self._find(key, None) is not None

    def __len__(self):
        """Gets the length of the Subject in terms of components."""
        return len(self._components)

    def __repr__(self):
        """Gets a internal representation of the Subject."""
        return f"{self.__class__.__name__}({self.__str__()})"

    def __str__(self):
        """Gets a string representation of the Subject."""
        return ",".join(map(lambda c: "=".join(c), self._components))

    def __eq__(self, other):
        """Tests the subject for equality with another Subject."""
        if isinstance(other, Subject):
            return self._components == other._components
        return False

    def __hash__(self):
        """Provides a hash code of the Subject."""
        return hash(self._components)

    ASSET_CLASS = "AssetClass"
    BUY_SIDE_ACCOUNT = "BuySideAccount"
    CURRENCY = "Currency"
    CURRENCY_PAIR = "Symbol"
    DEAL_TYPE = "DealType"
    EXCHANGE = "Exchange"
    EXPIRY_DATE = "ExpiryDate"
    FAR_CURRENCY = "FarCurrency"
    FAR_FIXING_DATE = "FarFixingDate"
    FAR_QUANTITY = "FarQuantity"
    FAR_SETTLEMENT_DATE = "FarSettlementDate"
    FAR_TENOR = "FarTenor"
    FIXING_CCY = "FixingCcy"
    FIXING_DATE = "FixingDate"
    LEVEL = "Level"
    LIQUIDITY_PROVIDER = "LiquidityProvider"
    ON_BEHALF_OF = "OnBehalfOf"
    PUT_CALL = "PutCall"
    QUANTITY = "Quantity"
    REQUEST_TYPE = "RequestFor"
    ROUTE = "Route"
    ROWS = "Rows"
    SETTLEMENT_DATE = "SettlementDate"
    SOURCE = "Source"
    STRIKE = "Strike"
    SYMBOL = "Symbol"
    TENOR = "Tenor"
    USER = "User"
