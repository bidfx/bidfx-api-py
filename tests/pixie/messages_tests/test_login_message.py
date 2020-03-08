import unittest

from bidfx.pricing._pixie.message.login_message import LoginMessage


class TestLoginMessage(unittest.TestCase):
    def setUp(self):
        self.login = "test_login"
        self.password = "test_password"
        self.alias = "test_alias"
        self.api = "bidfx-python-api"
        self.api_version = "0.0.1"
        self.product_serial = "some_serial"

        self.login_message = LoginMessage(
            self.login,
            self.password,
            self.alias,
            self.api,
            self.api_version,
            self.product_serial,
        )

    def test_decode(self):
        self.assertEqual(
            b"kL\x0btest_login\x0etest_password\x0btest_alias\x11bidfx-python-api\x060.0.1\x11bidfx-python-api\x060.0.1\x0cBidFXPython\x0csome_serial",
            self.login_message.to_bytes(),
        )

    def test_str_representation(self):
        self.assertEqual(
            str(self.login_message),
            f"LoginMessage Login:{self.login} Alias:{self.alias} ProductSerial:{self.product_serial}",
        )
