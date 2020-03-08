from .subject import Subject
from .tenor import Tenor
from ..exceptions import PricingError, InvalidSubjectError

__all__ = ["SubjectBuilder"]

CURRENCY_CODES = [
    "XAU",
    "XPT",
    "XPD",
    "XAG",
    "XDR",
    "EUR",
    "GBP",
    "AUD",
    "NZD",
    "USD",
    "CAD",
    "CHF",
    "NOK",
    "DKK",
    "SEK",
    "CLF",
    "KWD",
    "BHD",
    "OMR",
    "JOD",
    "FKP",
    "GIP",
    "SHP",
    "KYD",
    "CHE",
    "CUC",
    "BSD",
    "PAB",
    "BMD",
    "CUP",
    "CHW",
    "SGD",
    "BND",
    "LYD",
    "AZN",
    "ANG",
    "AWG",
    "BAM",
    "BGN",
    "BYN",
    "BBD",
    "BZD",
    "FJD",
    "TOP",
    "TND",
    "GEL",
    "WST",
    "XCD",
    "BRL",
    "PGK",
    "MXV",
    "PEN",
    "TMT",
    "QAR",
    "ILS",
    "AED",
    "TRY",
    "SAR",
    "PLN",
    "GHS",
    "RON",
    "MYR",
    "SDG",
    "TTD",
    "CNH",
    "CNY",
    "BOB",
    "HRK",
    "GTQ",
    "SRD",
    "HKD",
    "SBD",
    "MOP",
    "TJS",
    "SVC",
    "MAD",
    "VEF",
    "BWP",
    "ZAR",
    "SCR",
    "NAD",
    "LSL",
    "SZL",
    "ARS",
    "ERN",
    "MVR",
    "EGP",
    "MXN",
    "MDL",
    "ETB",
    "HNL",
    "CZK",
    "UAH",
    "UYI",
    "UYU",
    "NIO",
    "TWD",
    "THB",
    "MUR",
    "GMD",
    "DOP",
    "PHP",
    "RUB",
    "MKD",
    "BOV",
    "BTN",
    "INR",
    "AFN",
    "KGS",
    "HTG",
    "MZN",
    "SSP",
    "BDT",
    "LRD",
    "NPR",
    "KES",
    "CVE",
    "PKR",
    "VUV",
    "DZD",
    "ISK",
    "JPY",
    "XPF",
    "RSD",
    "ALL",
    "JMD",
    "LKR",
    "AOA",
    "DJF",
    "GYD",
    "COU",
    "YER",
    "HUF",
    "KZT",
    "NGN",
    "ZWL",
    "MRO",
    "KMF",
    "AMD",
    "SYP",
    "SOS",
    "CRC",
    "XAF",
    "XOF",
    "CLP",
    "MWK",
    "RWF",
    "KPW",
    "KRW",
    "IQD",
    "MMK",
    "CDF",
    "LBP",
    "BIF",
    "TZS",
    "MNT",
    "COP",
    "MGA",
    "UGX",
    "UZS",
    "KHR",
    "ZMW",
    "PYG",
    "SLL",
    "LAK",
    "GNF",
    "IDR",
    "VND",
    "STD",
    "IRR",
    "XSU",
    "XUA",
]


def _format_quantity(qty):
    try:
        f = float(qty)
        if f > 0:
            return "{:.2f}".format(f)
    except ValueError:
        pass
    raise InvalidSubjectError(
        "invalid quantity, positive number expected instead of: " + str(qty)
    )


def _validate_currency(ccy: str):
    if ccy not in CURRENCY_CODES:
        raise InvalidSubjectError(f'invalid ISO currency code: "{ccy}"')


def _validate_currency_pair(ccy_pair: str):
    if len(ccy_pair) == 6:
        ccy1 = ccy_pair[:3]
        ccy2 = ccy_pair[3:]
        if ccy1 != ccy2:
            if (ccy1 in CURRENCY_CODES) or (ccy2 in CURRENCY_CODES):
                return
    raise InvalidSubjectError(f'invalid currency pair code: "{ccy_pair}"')


def _validate_ccy_against_pair(ccy: str, ccy_pair: str):
    if ccy and ccy_pair:
        if ccy != ccy_pair[:3] and ccy != ccy_pair[3:]:
            raise InvalidSubjectError(
                f'currency "{ccy}" is not part of currency pair "{ccy_pair}"'
            )


def _validate_date(date) -> str:
    try:
        if int(date) > 19000101:
            return str(date)
    except ValueError:
        pass
    raise InvalidSubjectError(f'incorrectly formatted date "{date}", expected YYYYMMDD')


class SubjectFactory:
    def __init__(self):
        self._components = {Subject.LEVEL: "1"}
        self._mandatory_keys = {Subject.SYMBOL}

    def book(self, rows: int = None):
        self._components.update(
            {Subject.LIQUIDITY_PROVIDER: "FXTS", Subject.LEVEL: "2"}
        )
        if rows is not None:
            self._components[Subject.ROWS] = str(rows)
        return self

    def create_subject(self) -> Subject:
        self._validate_required_keys()
        return Subject.from_dict(self._components)

    def _validate_required_keys(self):
        missing_keys = self._mandatory_keys - self._components.keys()
        if missing_keys:
            raise InvalidSubjectError(
                f"incomplete subject is missing: {', '.join(sorted(missing_keys))}"
            )

    def _set_settlement_date(self, settlement_date_key, date):
        tenor_key = (
            Subject.FAR_TENOR
            if settlement_date_key == Subject.FAR_SETTLEMENT_DATE
            else Subject.TENOR
        )
        self._components[tenor_key] = self._components.get(tenor_key, Tenor.BROKEN_DATE)
        self._components[settlement_date_key] = _validate_date(date)

    def _set_fixing_date(self, fixing_date_key, date):
        self._components[fixing_date_key] = _validate_date(date)


class ListedSubject(SubjectFactory):
    def __init__(self, asset_class: str):
        super().__init__()
        self._components[Subject.ASSET_CLASS] = asset_class
        self._mandatory_keys.update({Subject.EXCHANGE, Subject.SOURCE})

    def source(self, source: str):
        self._components[Subject.SOURCE] = source
        return self

    def level(self, level: str):
        self._components[Subject.LEVEL] = level
        return self

    def exchange(self, exchange: str):
        self._components[Subject.EXCHANGE] = exchange
        return self

    def symbol(self, symbol: str):
        self._components[Subject.SYMBOL] = symbol
        return self


class SpotSubject(SubjectFactory):
    def __init__(self, components: dict):
        super().__init__()
        self._components.update(components)
        self._components[Subject.DEAL_TYPE] = "Spot"
        self._components[Subject.TENOR] = Tenor.SPOT
        self._mandatory_keys.update(
            {
                Subject.BUY_SIDE_ACCOUNT,
                Subject.CURRENCY,
                Subject.CURRENCY_PAIR,
                Subject.QUANTITY,
                Subject.LIQUIDITY_PROVIDER,
            }
        )

    def liquidity_provider(self, lp: str):
        self._components[Subject.LIQUIDITY_PROVIDER] = lp
        return self

    def currency_pair(self, ccy_pair: str):
        _validate_currency_pair(ccy_pair)
        _validate_ccy_against_pair(self._components.get(Subject.CURRENCY), ccy_pair)
        self._components[Subject.CURRENCY_PAIR] = ccy_pair
        return self

    def currency(self, ccy: str):
        _validate_currency(ccy)
        _validate_ccy_against_pair(ccy, self._components.get(Subject.CURRENCY_PAIR))
        self._components[Subject.CURRENCY] = ccy
        return self

    def quantity(self, qty: float):
        self._components[Subject.QUANTITY] = _format_quantity(qty)
        return self

    def buy_side_account(self, account_code: str):
        self._components[Subject.BUY_SIDE_ACCOUNT] = account_code
        return self

    def on_behalf_of(self, username: str):
        self._components[Subject.ON_BEHALF_OF] = username
        return self


class ForwardSubject(SubjectFactory):
    def __init__(self, components: dict, deliverable: bool):
        super().__init__()
        self._components.update(components)
        self._components[Subject.DEAL_TYPE] = "Outright" if deliverable else "NDF"
        self._mandatory_keys.update(
            {
                Subject.TENOR,
                Subject.BUY_SIDE_ACCOUNT,
                Subject.CURRENCY,
                Subject.CURRENCY_PAIR,
                Subject.DEAL_TYPE,
                Subject.QUANTITY,
                Subject.LIQUIDITY_PROVIDER,
            }
        )

    def liquidity_provider(self, lp: str):
        self._components[Subject.LIQUIDITY_PROVIDER] = lp
        return self

    def currency_pair(self, ccy_pair: str):
        _validate_currency_pair(ccy_pair)
        _validate_ccy_against_pair(self._components.get(Subject.CURRENCY), ccy_pair)
        self._components[Subject.CURRENCY_PAIR] = ccy_pair
        return self

    def currency(self, ccy: str):
        _validate_currency(ccy)
        _validate_ccy_against_pair(ccy, self._components.get(Subject.CURRENCY_PAIR))
        self._components[Subject.CURRENCY] = ccy
        return self

    def quantity(self, qty: float):
        self._components[Subject.QUANTITY] = _format_quantity(qty)
        return self

    def buy_side_account(self, account_code: str):
        self._components[Subject.BUY_SIDE_ACCOUNT] = account_code
        return self

    def tenor(self, tenor: str):
        self._components[Subject.TENOR] = tenor
        if tenor == Tenor.BROKEN_DATE:
            self._mandatory_keys.add(Subject.SETTLEMENT_DATE)
        return self

    def settlement_date(self, date):
        self._set_settlement_date(Subject.SETTLEMENT_DATE, date)
        return self

    def fixing_date(self, date):
        self._set_fixing_date(Subject.FIXING_DATE, date)
        return self

    def on_behalf_of(self, username: str):
        self._components[Subject.ON_BEHALF_OF] = username
        return self


class SwapSubject(SubjectFactory):
    def __init__(self, components: dict, deliverable: bool):
        super().__init__()
        self._components.update(components)
        self._components[Subject.DEAL_TYPE] = "Swap" if deliverable else "NDS"
        self._mandatory_keys.update(
            {
                Subject.TENOR,
                Subject.FAR_TENOR,
                Subject.FAR_QUANTITY,
                Subject.BUY_SIDE_ACCOUNT,
                Subject.CURRENCY,
                Subject.CURRENCY_PAIR,
                Subject.DEAL_TYPE,
                Subject.QUANTITY,
                Subject.LIQUIDITY_PROVIDER,
            }
        )

    def liquidity_provider(self, lp: str):
        self._components[Subject.LIQUIDITY_PROVIDER] = lp
        return self

    def currency_pair(self, ccy_pair: str):
        _validate_currency_pair(ccy_pair)
        _validate_ccy_against_pair(self._components.get(Subject.CURRENCY), ccy_pair)
        self._components[Subject.CURRENCY_PAIR] = ccy_pair
        return self

    def currency(self, ccy: str):
        _validate_currency(ccy)
        _validate_ccy_against_pair(ccy, self._components.get(Subject.CURRENCY_PAIR))
        self._components[Subject.CURRENCY] = ccy
        self._components[Subject.FAR_CURRENCY] = ccy
        return self

    def near_quantity(self, qty: float):
        self._components[Subject.QUANTITY] = _format_quantity(qty)
        return self

    def far_quantity(self, qty: float):
        self._components[Subject.FAR_QUANTITY] = _format_quantity(qty)
        return self

    def buy_side_account(self, account_code: str):
        self._components[Subject.BUY_SIDE_ACCOUNT] = account_code
        return self

    def near_tenor(self, tenor: str):
        self._components[Subject.TENOR] = tenor
        if tenor == Tenor.BROKEN_DATE:
            self._mandatory_keys.add(Subject.SETTLEMENT_DATE)
        return self

    def far_tenor(self, tenor: str):
        self._components[Subject.FAR_TENOR] = tenor
        if tenor == Tenor.BROKEN_DATE:
            self._mandatory_keys.add(Subject.FAR_SETTLEMENT_DATE)
        return self

    def near_settlement_date(self, date):
        self._set_settlement_date(Subject.SETTLEMENT_DATE, date)
        return self

    def far_settlement_date(self, date):
        self._set_settlement_date(Subject.FAR_SETTLEMENT_DATE, date)
        return self

    def near_fixing_date(self, date):
        self._set_fixing_date(Subject.FIXING_DATE, date)
        return self

    def far_fixing_date(self, date):
        self._set_fixing_date(Subject.FAR_FIXING_DATE, date)
        return self

    def on_behalf_of(self, username: str):
        self._components[Subject.ON_BEHALF_OF] = username
        return self


class DealableSubject:
    def __init__(self, components: dict):
        self._components = components

    @property
    def spot(self):
        return SpotSubject(self._components)

    @property
    def forward(self):
        return ForwardSubject(self._components, True)

    @property
    def ndf(self):
        return ForwardSubject(self._components, False)

    @property
    def swap(self):
        return SwapSubject(self._components, True)

    @property
    def nds(self):
        return SwapSubject(self._components, False)


class IndicativeSubjectCont(SubjectFactory):
    def __init__(self):
        super().__init__()
        self._components.update(
            {Subject.ASSET_CLASS: "Fx", Subject.EXCHANGE: "OTC", Subject.SOURCE: "Indi"}
        )

    def source(self, source: str):
        self._components[Subject.SOURCE] = source
        return self

    def currency_pair(self, ccy_pair: str):
        _validate_currency_pair(ccy_pair)
        self._components[Subject.CURRENCY_PAIR] = ccy_pair
        return self


class IndicativeSubject:
    @property
    def spot(self) -> IndicativeSubjectCont:
        return IndicativeSubjectCont()


class FxSubject:
    def __init__(self, username, default_account):
        self._username = username
        self._default_account = default_account

    @property
    def indicative(self) -> IndicativeSubject:
        return IndicativeSubject()

    @property
    def stream(self) -> DealableSubject:
        return DealableSubject(self._dealable_components("Stream"))

    @property
    def quote(self) -> DealableSubject:
        return DealableSubject(self._dealable_components("Quote"))

    def _dealable_components(self, request_type):
        components = {
            Subject.ASSET_CLASS: "Fx",
            Subject.REQUEST_TYPE: request_type,
            Subject.USER: self._username,
        }
        if self._default_account:
            components[Subject.BUY_SIDE_ACCOUNT] = self._default_account
        return components


class SubjectBuilder:
    """
    A SubjectBuilder provides a convenient way to construct a correctly formatted `Subject` by using
    a blend of method-chaining and the builder pattern. The method-chains guide the user to find a
    correct subject for common classes of instrument and the builder validates the results.
    """

    def __init__(self, username, default_account):
        if not username:
            raise PricingError("a username must be provided to subject builder")
        self._username = username
        self._default_account = default_account or None

    @property
    def fx(self) -> FxSubject:
        """
        Begins a method-chain for building an FX `Subject`.
        """
        return FxSubject(self._username, self._default_account)

    @property
    def future(self) -> ListedSubject:
        """
        Begins a method-chain for building a Future `Subject`.
        """
        return ListedSubject("Future")

    @property
    def equity(self) -> ListedSubject:
        """
        Begins a method-chain for building an Equity `Subject`.
        """
        return ListedSubject("Equity")
