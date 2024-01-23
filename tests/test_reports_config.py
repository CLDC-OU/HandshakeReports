import unittest
from config.files_config import FilesConfig
from config.reports_config import ReportsConfig
from dataset.appointment import AppointmentDataSet
from dataset.enrollment import EnrollmentDataSet
from dataset.referral import ReferralDataSet
from dataset.survey import SurveyDataSet
from src.reports.followup import Followup
from src.reports.referrals import Referrals
from src.reports.report import Report
from src.reports.survey_results import SurveyResults


class TestReportsConfig(unittest.TestCase):
    def test_init(self):
        self.test_cfg_1 = ReportsConfig("tests/test_files/test_reports_config.json", "tests/test_files/test_files_config.json")

        test_files_config = FilesConfig("tests/test_files/test_files_config.json")
        test_files_config.load_config()

        for i in range(len(test_files_config.files)):
            self.assertEqual(test_files_config.files[i].get_id(), self.test_cfg_1.get_files()[i].get_id())
            self.assertTrue(test_files_config.files[i].get_df().equals(self.test_cfg_1.get_files()[i].get_df()))

        self.assertEqual(len(self.test_cfg_1.get_appointments()), 1)
        self.assertIsNotNone(self.test_cfg_1.get_enrollment())
        self.assertEqual(len(self.test_cfg_1.get_files()), 4)
        self.assertEqual(len(self.test_cfg_1.get_referrals()), 1)
        self.assertEqual(len(self.test_cfg_1.get_survey_results()), 1)

        self.assertEqual(self.test_cfg_1.get_appointments()[0].get_id(), "test_appointments")

        for i in range(len(self.test_cfg_1.get_appointments())):
            self.assertIsInstance(self.test_cfg_1.get_appointments()[i], AppointmentDataSet)
        for i in range(len(self.test_cfg_1.get_referrals())):
            self.assertIsInstance(self.test_cfg_1.get_appointments()[i], ReferralDataSet)
        for i in range(len(self.test_cfg_1.get_survey_results())):
            self.assertIsInstance(self.test_cfg_1.get_appointments()[i], SurveyDataSet)
        self.assertIsInstance(self.test_cfg_1.get_enrollment(), EnrollmentDataSet)

    def test_get_survey_by_id(self):
        self.assertEqual(self.test_cfg_1.get_survey_by_id("test_survey_results"), self.test_cfg_1.get_survey_results()[0])
        self.assertIsNone(self.test_cfg_1.get_survey_by_id("test_survey_results_2"))

    def test_load_reports(self):
        self.test_cfg_1.load_reports()
        self.assertIsNotNone(self.test_cfg_1.get_reports())
        self.assertEqual(len(self.test_cfg_1.get_reports()), 3)

        report = self.test_cfg_1.get_reports()[0]
        self.assertIsInstance(report, Report)
        self.assertEqual(report.file_prefix, "test_survey_results_")
        self.assertIsInstance(report.report, SurveyResults)
        self.assertEqual(report.report._staff_emails, ["test1@email.com", "test2@email.com", "test3@email.com", "testnone@email.com"])  # type: ignore
        self.assertEqual(report.report._day_range, 4)  # type: ignore
        self.assertEqual(report.report._years, "2023, 2024")  # type: ignore
        self.assertEqual(report.report._months, "August-December", "January-May")  # type: ignore

        report = self.test_cfg_1.get_reports()[1]
        self.assertIsInstance(report, Report)
        self.assertEqual(report.file_prefix, "test_followup_")
        self.assertIsInstance(report.report, Followup)

        report = self.test_cfg_1.get_reports()[2]
        self.assertIsInstance(report, Report)
        self.assertEqual(report.file_prefix, "test_referrals_")
        self.assertIsInstance(report.report, Referrals)

    def test_run_reports(self):
        self.test_cfg_1.run_reports()

        test_results = self.test_cfg_1.get_reports()[0].report.get_results()
