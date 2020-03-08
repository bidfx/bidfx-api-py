import unittest

from bidfx.pricing._subject_builder import SubjectBuilder


class TestPuffinSubjects(unittest.TestCase):
    def setUp(self):
        username = "jbloggs"
        default_account = "MY_ACCT"
        self.subject_builder = SubjectBuilder(username, default_account)

    def test_subject_messages(self):
        self.assertEqual(
            str(
                self.subject_builder.future.exchange("EUX")
                .source("Delayed")
                .symbol("F:FOAT\\Z18")
                .create_subject()
            ),
            "AssetClass=Future,Exchange=EUX,Level=1,Source=Delayed,Symbol=F:FOAT\\Z18",
        )

        self.assertEqual(
            "AssetClass=Fx,Exchange=OTC,Level=1,Source=Indi,Symbol=EURGBP",
            str(
                self.subject_builder.fx.indicative.spot.currency_pair(
                    "EURGBP"
                ).create_subject()
            ),
        )
