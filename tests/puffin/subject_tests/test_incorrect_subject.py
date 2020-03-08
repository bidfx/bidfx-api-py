import unittest

from bidfx import InvalidSubjectError
from bidfx.pricing._subject_builder import SubjectBuilder


class TestPuffinIncorrectSubjects(unittest.TestCase):
    def setUp(self):
        username = "jbloggs"
        default_account = "MY_ACCT"
        self.subject_builder = SubjectBuilder(username, default_account)

    def test_exceptions_in_subject_messages_missing_symbol(self):
        with self.assertRaises(InvalidSubjectError) as error:
            self.subject_builder.fx.indicative.spot.create_subject()
        self.assertEqual(str(error.exception), "incomplete subject is missing: Symbol")
