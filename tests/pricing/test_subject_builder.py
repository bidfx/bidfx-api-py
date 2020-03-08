from unittest import TestCase

from bidfx import Tenor, PricingError, InvalidSubjectError
from bidfx.pricing._subject_builder import SubjectBuilder

USERNAME = "jbloggs"
DEFAULT_ACCOUNT = "MYACCT"


class TestFxSpotSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_fx_spot_stream_euro(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=CSFX,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .create_subject()
            ),
        )

    def test_fx_spot_stream_cable(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=GBP,DealType=Spot,Level=1,LiquidityProvider=BARCFX,"
            "Quantity=543219.07,RequestFor=Stream,Symbol=GBPUSD,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.currency("GBP")
                .quantity(543219.07)
                .currency_pair("GBPUSD")
                .liquidity_provider("BARCFX")
                .create_subject()
            ),
        )

    def test_fx_spot_stream_with_non_default_account(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=METALS_ACC1,Currency=XAU,DealType=Spot,Level=1,LiquidityProvider=RBSFX,"
            "Quantity=23000.00,RequestFor=Stream,Symbol=XAUUSD,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.buy_side_account("METALS_ACC1")
                .currency_pair("XAUUSD")
                .currency("XAU")
                .quantity(23000)
                .liquidity_provider("RBSFX")
                .create_subject()
            ),
        )

    def test_fx_spot_quote(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=CSFX,"
            "Quantity=1000000.00,RequestFor=Quote,Symbol=EURGBP,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.quote.spot.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .create_subject()
            ),
        )


class TestFxSpotSubjectErrorHandling(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_fx_spot_stream_missing_quantity(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency("GBP").currency_pair(
                "EURGBP"
            ).currency("EUR").liquidity_provider("CSFX").create_subject()
        self.assertEqual(
            "incomplete subject is missing: Quantity", str(error.exception)
        )

    def test_currency_must_be_part_of_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            str(
                self.subject_builder.fx.quote.spot.currency_pair("EURGBP")
                .currency("MXN")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .create_subject()
            )
        self.assertEqual(
            'currency "MXN" is not part of currency pair "EURGBP"', str(error.exception)
        )

    def test_currency_must_be_valid_iso_code(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.spot.currency_pair("EURUSD").currency(
                "US$"
            ).quantity(1000000).liquidity_provider("CSFX").create_subject()
        self.assertEqual('invalid ISO currency code: "US$"', str(error.exception))

    def test_currency_pair_must_be_valid_iso_code(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.spot.currency_pair("EUR/GBP").currency(
                "EUR"
            ).quantity(1000000).liquidity_provider("CSFX").create_subject()
        self.assertEqual('invalid currency pair code: "EUR/GBP"', str(error.exception))

    def test_quantity_must_not_be_zero(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("EURGBP").currency(
                "EUR"
            ).quantity(0).liquidity_provider("CSFX").create_subject()
        self.assertEqual(
            "invalid quantity, positive number expected instead of: 0",
            str(error.exception),
        )

    def test_quantity_must_not_be_negative(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("EURGBP").currency(
                "EUR"
            ).quantity(-1000000).liquidity_provider("CSFX").create_subject()
        self.assertEqual(
            "invalid quantity, positive number expected instead of: -1000000",
            str(error.exception),
        )

    def test_fx_spot_stream_missing_quantity_and_currency(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair(
                "EURGBP"
            ).liquidity_provider("CSFX").create_subject()
        self.assertEqual(
            "incomplete subject is missing: Currency, Quantity", str(error.exception)
        )

    def test_invalid_quantity(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.quantity(-200)
        self.assertEqual(
            "invalid quantity, positive number expected instead of: -200",
            str(error.exception),
        )
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.quantity("$25m")
        self.assertEqual(
            "invalid quantity, positive number expected instead of: $25m",
            str(error.exception),
        )

    def test_invalid_currency(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency("$US")
        self.assertEqual('invalid ISO currency code: "$US"', str(error.exception))

    def test_invalid_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("GPBEur")
        self.assertEqual('invalid currency pair code: "GPBEur"', str(error.exception))

    def test_currency_pair_with_same_two_currencies(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("EUREUR")
        self.assertEqual('invalid currency pair code: "EUREUR"', str(error.exception))

    def test_invalid_currency_and_pair_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("EURGBP").currency("USD")
        self.assertEqual(
            'currency "USD" is not part of currency pair "EURGBP"', str(error.exception)
        )

    def test_invalid_currency_pair_and_currency_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("USDCAD").currency("MXN")
        self.assertEqual(
            'currency "MXN" is not part of currency pair "USDCAD"', str(error.exception)
        )


class TestFxForwardSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_stream_with_month_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=CSFX,Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .tenor(Tenor.of_month(1))
                .create_subject()
            ),
        )

    def test_stream_with_spot_next_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=BARC,Quantity=500000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=S/N,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(500000)
                .liquidity_provider("BARC")
                .tenor(Tenor.SPOT_NEXT)
                .create_subject()
            ),
        )

    def test_stream_with_broken_date_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=CSFX,Quantity=3500000.00,RequestFor=Stream,SettlementDate=20180918,"
            "Symbol=EURGBP,Tenor=BD,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .quantity(3500000)
                .currency("EUR")
                .settlement_date(20180918)
                .tenor(Tenor.BROKEN_DATE)
                .create_subject()
            ),
        )

    def test_stream_with_broken_date_as_default(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=CSFX,Quantity=3500000.00,RequestFor=Stream,SettlementDate=20180918,"
            "Symbol=EURGBP,Tenor=BD,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .quantity(3500000)
                .currency("EUR")
                .settlement_date("20180918")
                .create_subject()
            ),
        )

    def test_stream_with_tenor_and_settlement(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=CSFX,Quantity=3500000.00,RequestFor=Stream,SettlementDate=20190918,"
            "Symbol=EURGBP,Tenor=1Y,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .quantity(3500000)
                .currency("EUR")
                .settlement_date(20190918)
                .tenor(Tenor.of_year(1))
                .create_subject()
            ),
        )

    def test_stream_with_month_tenor_and_account(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=BLACK-ACCOUNT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=CSFX,Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.buy_side_account("BLACK-ACCOUNT")
                .currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .tenor(Tenor.of_month(1))
                .create_subject()
            ),
        )

    def test_stream_on_behalf_of_another_user(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=1,"
            "LiquidityProvider=XTX,OnBehalfOf=jbloggs,Quantity=1000000.00,RequestFor=Stream,"
            "Symbol=EURGBP,Tenor=TOD,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("XTX")
                .tenor(Tenor.TODAY)
                .on_behalf_of("jbloggs")
                .create_subject()
            ),
        )


class TestFxForwardSubjectErrorHandling(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_fx_fwd_stream_missing_LP(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.currency_pair("EURGBP").quantity(
                3500000
            ).currency("EUR").settlement_date("20190918").tenor(
                Tenor.of_year(1)
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: LiquidityProvider", str(error.exception)
        )

    def test_fx_fwd_stream_missing_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.liquidity_provider("CSFX").quantity(
                3500000
            ).currency("EUR").settlement_date("20190918").tenor(
                Tenor.of_year(1)
            ).create_subject()
        self.assertEqual("incomplete subject is missing: Symbol", str(error.exception))

    def test_fx_fwd_stream_missing_quantity(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.liquidity_provider(
                "CSFX"
            ).currency_pair("EURGBP").currency("EUR").settlement_date(
                "20190918"
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: Quantity", str(error.exception)
        )

    def test_fx_fwd_stream_missing_broken_tenor(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.liquidity_provider(
                "CSFX"
            ).currency_pair("EURGBP").quantity(3500000).currency("EUR").create_subject()
            self.assertEqual(
                "incomplete subject is missing: Tenor", str(error.exception)
            )

    def test_fx_fwd_stream_missing_broken_settlement_date(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.liquidity_provider(
                "CSFX"
            ).currency_pair("EURGBP").quantity(3500000).currency("EUR").tenor(
                Tenor.BROKEN_DATE
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: SettlementDate", str(error.exception)
        )

    def test_invalid_currency(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.currency("$US")
        self.assertEqual('invalid ISO currency code: "$US"', str(error.exception))

    def test_invalid_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.currency_pair("GPBEur")
        self.assertEqual('invalid currency pair code: "GPBEur"', str(error.exception))

    def test_invalid_currency_and_pair_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.currency_pair("EURGBP").currency(
                "USD"
            )
        self.assertEqual(
            'currency "USD" is not part of currency pair "EURGBP"', str(error.exception)
        )

    def test_invalid_currency_pair_and_currency_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.currency_pair("USDCAD").currency(
                "MXN"
            )
        self.assertEqual(
            'currency "MXN" is not part of currency pair "USDCAD"', str(error.exception)
        )

    def test_invalid_settlement_date_string(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.settlement_date("2020-01-08")
        self.assertEqual(
            'incorrectly formatted date "2020-01-08", expected YYYYMMDD',
            str(error.exception),
        )

    def test_invalid_settlement_date_number(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.settlement_date(2019)
        self.assertEqual(
            'incorrectly formatted date "2019", expected YYYYMMDD', str(error.exception)
        )


class TestFXSwapSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_stream_with_month_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=1000000.00,FarTenor=3M,Level=1,LiquidityProvider=CSFX,Quantity=1000000.00,"
            "RequestFor=Quote,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.quote.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(1000000)
                .near_tenor(Tenor.of_month(1))
                .far_quantity(1000000)
                .far_tenor(Tenor.of_month(3))
                .create_subject()
            ),
        )

    def test_stream_with_broken_date_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=3500000.00,FarSettlementDate=20181218,FarTenor=BD,Level=1,"
            "LiquidityProvider=CSFX,Quantity=3500000.00,RequestFor=Quote,SettlementDate=20180918,"
            "Symbol=EURGBP,Tenor=BD,User=jbloggs",
            str(
                self.subject_builder.fx.quote.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(3500000)
                .near_settlement_date(20180918)
                .near_tenor(Tenor.BROKEN_DATE)
                .far_quantity(3500000)
                .far_settlement_date(20181218)
                .far_tenor(Tenor.BROKEN_DATE)
                .create_subject()
            ),
        )

    def test_stream_with_broken_date_as_default(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=3500000.00,FarSettlementDate=20181018,FarTenor=BD,Level=1,"
            "LiquidityProvider=CSFX,Quantity=3500000.00,RequestFor=Stream,SettlementDate=20180918,"
            "Symbol=EURGBP,Tenor=BD,User=jbloggs",
            str(
                self.subject_builder.fx.stream.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(3500000)
                .near_settlement_date("20180918")
                .far_quantity(3500000)
                .far_settlement_date("20181018")
                .create_subject()
            ),
        )

    def test_stream_with_tenor_and_settlement(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=3500000.00,FarSettlementDate=20181223,FarTenor=3M,Level=1,LiquidityProvider=CSFX,"
            "Quantity=3500000.00,RequestFor=Stream,SettlementDate=20180915,Symbol=EURGBP,Tenor=3W,User=jbloggs",
            str(
                self.subject_builder.fx.stream.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(3500000)
                .near_settlement_date("20180915")
                .near_tenor(Tenor.of_week(3))
                .far_quantity(3500000)
                .far_settlement_date("20181223")
                .far_tenor(Tenor.of_month(3))
                .create_subject()
            ),
        )

    def test_stream_with_month_tenor_and_account(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=SPECIAL123,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=1000000.00,FarTenor=3M,Level=1,LiquidityProvider=CSFX,Quantity=1000000.00,"
            "RequestFor=Stream,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(1000000)
                .near_tenor(Tenor.of_month(1))
                .far_quantity(1000000)
                .far_tenor(Tenor.of_month(3))
                .buy_side_account("SPECIAL123")
                .create_subject()
            ),
        )

    def test_stream_on_behalf_of_another_user(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Swap,FarCurrency=EUR,"
            "FarQuantity=1000000.00,FarTenor=IMMU,Level=1,LiquidityProvider=CSFX,OnBehalfOf=weejimmy,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.swap.liquidity_provider("CSFX")
                .currency_pair("EURGBP")
                .currency("EUR")
                .near_quantity(1000000)
                .near_tenor(Tenor.of_month(1))
                .far_quantity(1000000)
                .far_tenor(Tenor.IMM_SEPTEMBER)
                .on_behalf_of("weejimmy")
                .create_subject()
            ),
        )


class TestFXSwapSubjectErrorHandling(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_stream_missing_LP(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.swap.currency_pair("EURGBP").currency(
                "EUR"
            ).near_quantity(3500000).near_settlement_date("20190318").near_tenor(
                Tenor.of_month(6)
            ).far_quantity(
                3500000
            ).far_settlement_date(
                "20190918"
            ).far_tenor(
                Tenor.of_year(1)
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: LiquidityProvider", str(error.exception)
        )

    def test_stream_missing_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.liquidity_provider("CSFX").currency(
                "EUR"
            ).near_quantity(3500000).far_quantity(3000000).near_settlement_date(
                "20190918"
            ).near_tenor(
                Tenor.of_year(1)
            ).far_tenor(
                Tenor.of_year(2)
            ).create_subject()
            self.assertEqual(
                "incomplete subject is missing: Symbol", str(error.exception)
            )

    def test_stream_missing_far_quantity_and_tenor(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.swap.liquidity_provider(
                "CSFX"
            ).currency_pair("EURGBP").currency("EUR").near_quantity(
                3500000
            ).near_settlement_date(
                "20190918"
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: FarQuantity, FarTenor", str(error.exception)
        )

    def test_stream_missing_far_leg(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.liquidity_provider("CSFX").currency_pair(
                "EURGBP"
            ).currency("EUR").near_quantity(3500000).near_tenor(
                Tenor.of_year(1)
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: FarQuantity, FarTenor", str(error.exception)
        )

    def test_invalid_quantity(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.near_quantity(-200)
        self.assertEqual(
            "invalid quantity, positive number expected instead of: -200",
            str(error.exception),
        )
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.swap.far_quantity("$25m")
        self.assertEqual(
            "invalid quantity, positive number expected instead of: $25m",
            str(error.exception),
        )

    def test_invalid_currency(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.swap.currency("$US")
        self.assertEqual('invalid ISO currency code: "$US"', str(error.exception))

    def test_invalid_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.currency_pair("GPBEur")
        self.assertEqual('invalid currency pair code: "GPBEur"', str(error.exception))

    def test_invalid_currency_and_pair_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.currency_pair("EURGBP").currency("USD")
        self.assertEqual(
            'currency "USD" is not part of currency pair "EURGBP"', str(error.exception)
        )

    def test_invalid_currency_pair_and_currency_combo(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.currency_pair("USDCAD").currency("MXN")
        self.assertEqual(
            'currency "MXN" is not part of currency pair "USDCAD"', str(error.exception)
        )

    def test_invalid_settlement_date_string(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.near_settlement_date("2020-01-08")
        self.assertEqual(
            'incorrectly formatted date "2020-01-08", expected YYYYMMDD',
            str(error.exception),
        )

    def test_invalid_settlement_date_number(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.quote.swap.far_settlement_date(2019)
        self.assertEqual(
            'incorrectly formatted date "2019", expected YYYYMMDD', str(error.exception)
        )


class TestFxNdfSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_stream_with_tenor(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=NDF,Level=1,LiquidityProvider=CSFX,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.ndf.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .tenor(Tenor.of_month(1))
                .create_subject()
            ),
        )

    def test_stream_with_tenor_and_settlement(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=NDF,Level=1,LiquidityProvider=CSFX,"
            "Quantity=1000000.00,RequestFor=Stream,SettlementDate=20180923,Symbol=EURGBP,Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.ndf.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .tenor(Tenor.of_month(1))
                .settlement_date("20180923")
                .create_subject()
            ),
        )

    def test_stream_with_tenor_and_settlement_and_fixing(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=NDF,FixingDate=20190921,Level=1,"
            "LiquidityProvider=CSFX,Quantity=1000000.00,RequestFor=Stream,SettlementDate=20190923,"
            "Symbol=EURGBP,Tenor=1Y,User=jbloggs",
            str(
                self.subject_builder.fx.stream.ndf.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .tenor(Tenor.of_year(1))
                .settlement_date("20190923")
                .fixing_date("20190921")
                .create_subject()
            ),
        )


class TestNdsSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_nds_with_tenors(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=USD,DealType=NDS,FarCurrency=USD,FarQuantity=850000.00,"
            "FarTenor=3M,Level=1,LiquidityProvider=CSFX,Quantity=1000000.00,RequestFor=Stream,Symbol=USDCNY,"
            "Tenor=1M,User=jbloggs",
            str(
                self.subject_builder.fx.stream.nds.liquidity_provider("CSFX")
                .currency_pair("USDCNY")
                .currency("USD")
                .near_quantity(1000000)
                .near_tenor(Tenor.of_month(1))
                .far_quantity(850000)
                .far_tenor(Tenor.of_month(3))
                .create_subject()
            ),
        )

    def test_nds_with_explicit_dates(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=USD,DealType=NDS,FarCurrency=USD,FarFixingDate=20190308,"
            "FarQuantity=850000.00,FarSettlementDate=20190310,FarTenor=BD,FixingDate=20180915,Level=1,"
            "LiquidityProvider=CSFX,Quantity=1000000.00,RequestFor=Stream,SettlementDate=20180918,Symbol=USDCNY,"
            "Tenor=BD,User=jbloggs",
            str(
                self.subject_builder.fx.stream.nds.liquidity_provider("CSFX")
                .currency_pair("USDCNY")
                .currency("USD")
                .near_quantity(1000000)
                .near_tenor(Tenor.BROKEN_DATE)
                .near_fixing_date("20180915")
                .near_settlement_date(20180918)
                .far_quantity(850000)
                .far_tenor(Tenor.BROKEN_DATE)
                .far_fixing_date("20190308")
                .far_settlement_date("20190310")
                .create_subject()
            ),
        )


class TestOnBehalfOfSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder("admin", DEFAULT_ACCOUNT)

    def test_fx_spot_stream(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=CSFX,"
            "OnBehalfOf=jbloggs,Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=Spot,User=admin",
            str(
                self.subject_builder.fx.stream.spot.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .on_behalf_of(USERNAME)
                .create_subject()
            ),
        )
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Spot,Level=1,LiquidityProvider=CSFX,"
            "OnBehalfOf=akilroy,Quantity=1000000.00,RequestFor=Stream,Symbol=EURGBP,Tenor=Spot,User=admin",
            str(
                self.subject_builder.fx.stream.spot.currency_pair("EURGBP")
                .currency("EUR")
                .quantity(1000000)
                .liquidity_provider("CSFX")
                .on_behalf_of("akilroy")
                .create_subject()
            ),
        )


class TestFxTopOfBook(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_fx_spot_book(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Spot,Level=2,LiquidityProvider=FXTS,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=EURUSD,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.book()
                .currency_pair("EURUSD")
                .currency("EUR")
                .quantity(1000000)
                .create_subject()
            ),
        )

        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=GBP,DealType=Spot,Level=2,LiquidityProvider=FXTS,"
            "Quantity=543219.50,RequestFor=Stream,Rows=3,Symbol=GBPUSD,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.book(3)
                .currency("GBP")
                .quantity(543219.5)
                .currency_pair("GBPUSD")
                .create_subject()
            ),
        )

    def test_fx_forward_book(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=EUR,DealType=Outright,Level=2,LiquidityProvider=FXTS,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=EURUSD,Tenor=3W,User=jbloggs",
            str(
                self.subject_builder.fx.stream.forward.book()
                .currency_pair("EURUSD")
                .currency("EUR")
                .quantity(1000000)
                .tenor(Tenor.of_week(3))
                .create_subject()
            ),
        )

    def test_fx_ndf_book(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=MYACCT,Currency=USD,DealType=NDF,Level=2,LiquidityProvider=FXTS,"
            "Quantity=1000000.00,RequestFor=Stream,Symbol=USDKRW,Tenor=IMMH,User=jbloggs",
            str(
                self.subject_builder.fx.stream.ndf.book()
                .currency_pair("USDKRW")
                .currency("USD")
                .quantity(1000000)
                .tenor(Tenor.of_imm_month(3))
                .create_subject()
            ),
        )

    def test_fx_forward_book_missing_tenor(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.forward.book().currency_pair(
                "EURUSD"
            ).currency("EUR").quantity(1000000).create_subject()
        self.assertEqual("incomplete subject is missing: Tenor", str(error.exception))

    def test_fx_ndf_book_missing_tennor(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.ndf.book().currency_pair("EURUSD").currency(
                "EUR"
            ).quantity(1000000).create_subject()
        self.assertEqual("incomplete subject is missing: Tenor", str(error.exception))


class TestFutureSubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_future(self):
        self.assertEqual(
            "AssetClass=Future,Exchange=CBO,Level=1,Source=ComStock,Symbol=F2:VX\\V18",
            str(
                self.subject_builder.future.source("ComStock")
                .exchange("CBO")
                .symbol("F2:VX\\V18")
                .create_subject()
            ),
        )

    def test_future_change_source(self):
        self.assertEqual(
            "AssetClass=Future,Exchange=EUX,Level=1,Source=Delayed,Symbol=F:FOAT\\Z18",
            str(
                self.subject_builder.future.exchange("EUX")
                .source("Delayed")
                .symbol("F:FOAT\\Z18")
                .create_subject()
            ),
        )

    def test_future_market_depth(self):
        self.assertEqual(
            "AssetClass=Future,Exchange=GBX,Level=Depth,Source=ComStock,Symbol=F2:RP\\Z18",
            str(
                self.subject_builder.future.exchange("GBX")
                .level("Depth")
                .source("ComStock")
                .symbol("F2:RP\\Z18")
                .create_subject()
            ),
        )

    def test_future_missing_exchange(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.future.source("ComStock").symbol(
                "E:VOD"
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: Exchange", str(error.exception)
        )

    def test_future_missing_symbol(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.future.exchange("LSE").source(
                "ComStock"
            ).create_subject()
        self.assertEqual("incomplete subject is missing: Symbol", str(error.exception))


class TestEquitySubjectCreation(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_equity(self):
        self.assertEqual(
            "AssetClass=Equity,Exchange=LSE,Level=1,Source=BBG,Symbol=VOD:LN",
            str(
                self.subject_builder.equity.exchange("LSE")
                .source("BBG")
                .symbol("VOD:LN")
                .create_subject()
            ),
        )

    def test_equity_change_source(self):
        self.assertEqual(
            "AssetClass=Equity,Exchange=LSE,Level=1,Source=Reuters,Symbol=VOD.L",
            str(
                self.subject_builder.equity.exchange("LSE")
                .source("Reuters")
                .symbol("VOD.L")
                .create_subject()
            ),
        )

    def test_equity_market_depth(self):
        self.assertEqual(
            "AssetClass=Equity,Exchange=LSE,Level=Depth,Source=Reuters,Symbol=VOD.L",
            str(
                self.subject_builder.equity.exchange("LSE")
                .level("Depth")
                .source("Reuters")
                .symbol("VOD.L")
                .create_subject()
            ),
        )

    def test_equity_missing_exchange(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.equity.source("ComStock").symbol(
                "E:VOD"
            ).create_subject()
        self.assertEqual(
            "incomplete subject is missing: Exchange", str(error.exception)
        )

    def test_equity_missing_symbol(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.equity.exchange("LSE").source(
                "ComStock"
            ).create_subject()
        self.assertEqual("incomplete subject is missing: Symbol", str(error.exception))


class TestFxIndicative(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, DEFAULT_ACCOUNT)

    def test_fx_spot(self):
        self.assertEqual(
            "AssetClass=Fx,Exchange=OTC,Level=1,Source=Indi,Symbol=EURGBP",
            str(
                self.subject_builder.fx.indicative.spot.currency_pair(
                    "EURGBP"
                ).create_subject()
            ),
        )
        self.assertEqual(
            "AssetClass=Fx,Exchange=OTC,Level=1,Source=Indi,Symbol=GBPJPY",
            str(
                self.subject_builder.fx.indicative.spot.currency_pair(
                    "GBPJPY"
                ).create_subject()
            ),
        )

    def test_fx_spot_without_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.indicative.spot.create_subject()
        self.assertEqual("incomplete subject is missing: Symbol", str(error.exception))

    def test_fx_spot_with_bad_currency_pair(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.indicative.spot.currency_pair("cable")
        self.assertEqual('invalid currency pair code: "cable"', str(error.exception))


class TestWithoutDefaultAccount(TestCase):
    def setUp(self):
        self.subject_builder = SubjectBuilder(USERNAME, None)

    def test_no_account_specified_results_in_error(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.stream.spot.currency_pair("EURGBP").currency(
                "EUR"
            ).quantity(1000000).liquidity_provider("CSFX").create_subject()
        self.assertEqual(
            "incomplete subject is missing: BuySideAccount", str(error.exception)
        )

    def test_specified_account_is_used(self):
        self.assertEqual(
            "AssetClass=Fx,BuySideAccount=ABCD,Currency=GBP,DealType=Spot,Level=1,LiquidityProvider=BARCFX,"
            "Quantity=543219.07,RequestFor=Stream,Symbol=GBPUSD,Tenor=Spot,User=jbloggs",
            str(
                self.subject_builder.fx.stream.spot.currency("GBP")
                .quantity(543219.07)
                .currency_pair("GBPUSD")
                .buy_side_account("ABCD")
                .liquidity_provider("BARCFX")
                .create_subject()
            ),
        )


class TestWithoutUsername(TestCase):
    def test_blank_user_specified_results_in_error(self):
        with self.assertRaises(PricingError) as error:
            SubjectBuilder("", DEFAULT_ACCOUNT)
        self.assertEqual(
            "a username must be provided to subject builder", str(error.exception)
        )

    def test_none_user_specified_results_in_error(self):
        with self.assertRaises(PricingError) as error:
            SubjectBuilder(None, DEFAULT_ACCOUNT)
        self.assertEqual(
            "a username must be provided to subject builder", str(error.exception)
        )
