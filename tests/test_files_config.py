import unittest
from config.files_config import FilesConfig
from dataset.appointment import AppointmentDataSet
from dataset.enrollment import EnrollmentDataSet
from dataset.referral import ReferralDataSet
from dataset.survey import SurveyDataSet


class TestFilesConfig(unittest.TestCase):
    def test_load(self):
        test_cfg_1 = FilesConfig("tests/test_files/test_files_config.json")
        print(test_cfg_1.load_config())
        print(test_cfg_1.config)
        print(test_cfg_1.files)
        self.assertIsNotNone(test_cfg_1.config)
        self.assertIsNotNone(test_cfg_1.files)
        self.assertEqual(len(test_cfg_1.files), 4)

        self.assertIsInstance(test_cfg_1.files[0], AppointmentDataSet)
        self.assertEqual(test_cfg_1.files[0].get_id(), "test_appointments")
        self.assertEqual(test_cfg_1.files[0].cols[0], "Appointment Start Date")
        self.assertEqual(test_cfg_1.files[0].cols[1], "Appointment Type")
        self.assertEqual(test_cfg_1.files[0].cols[2], "Student College")
        self.assertEqual(test_cfg_1.files[0].cols[3], "Student Class Standing")
        self.assertEqual(test_cfg_1.files[0].cols[4], "Appointments Status")
        self.assertEqual(test_cfg_1.files[0].cols[5], "Student Last Name")
        self.assertEqual(test_cfg_1.files[0].cols[6], "Student First Name")
        self.assertEqual(test_cfg_1.files[0].cols[7], "Date Appointmet Scheduled")
        self.assertEqual(test_cfg_1.files[0].get_col_name(AppointmentDataSet.Column.DATE), "Appointment Start Date")

        self.assertIsInstance(test_cfg_1.files[1], SurveyDataSet)
        self.assertEqual(test_cfg_1.files[1].id, "test_survey_results")

        self.assertIsInstance(test_cfg_1.files[2], EnrollmentDataSet)
        self.assertEqual(test_cfg_1.files[2].id, "test_enrollment")

        self.assertIsInstance(test_cfg_1.files[3], ReferralDataSet)
        self.assertEqual(test_cfg_1.files[3].id, "test_referral")
