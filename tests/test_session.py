from configparser import ConfigParser
from unittest import TestCase

from bidfx import Session

VERSION = "0.5.0"


class TestSession(TestCase):
    def test_version(self):
        self.assertEqual(VERSION, Session.version())
