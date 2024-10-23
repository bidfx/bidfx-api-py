from configparser import ConfigParser
from unittest import TestCase

from bidfx import Session

VERSION = "1.1.3"


class TestSession(TestCase):
    def test_version(self):
        self.assertEqual(VERSION, Session.version())
