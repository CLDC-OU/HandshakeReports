import json
import logging
from src.config.config import Config
from src.config.files_config import FilesConfig

from src.reports.followup import Followup
from src.reports.referrals import Referrals
from src.reports.report import Report
from src.dataset.appointment import AppointmentDataSet
from src.dataset.dataset import DataSet
from src.dataset.enrollment import EnrollmentDataSet
from src.dataset.referral import ReferralDataSet
from src.dataset.survey import SurveyDataSet
from src.reports.survey_results import SurveyResults
from src.utils.type_utils import FilterType

REPORTS_CONFIG_FILE = "reports.config.json"


class ReportsConfig(Config):
    def __init__(self, config_file: str = REPORTS_CONFIG_FILE, files_config_file: str | None = None) -> None:
        super().__init__(config_file)
        if files_config_file:
            self._files = FilesConfig(files_config_file)
        else:
            self._files = FilesConfig()
        self._referrals = None
        self._surveys = None
        self._appointments = None
        self._enrollment = None
        self.config_file = config_file
        try:
            with open(config_file) as json_file:
                self.config = json.load(json_file)
            logging.debug("Reports config loaded")
        except Exception as e:
            logging.warning(f"WARNING! Could not find {self.config_file}: "
                            f"{str(e)}")
            self.config = None
        finally:
            self._reports = None
            if files_config_file:
                self._files = FilesConfig(files_config_file)
            else:
                self._files = FilesConfig()
            self._files.load_config()
        self.load_files()

    def get_files(self) -> list[DataSet]:
        if not self._files:
            raise ValueError("FilesConfig not initialized")
        return self._files.files

    def get_reports(self) -> list[Report]:
        if not self._reports:
            raise ValueError("Reports not initialized")
        return self._reports

    def load_config(self):
        super().load_config()
        self.load_files()

    def load_files(self):
        self._appointments = []
        self._surveys = []
        self._enrollment = None
        self._referrals = []
        for file in self.get_files():
            if isinstance(file, AppointmentDataSet):
                self._appointments.append(file)
            elif isinstance(file, EnrollmentDataSet):
                self._enrollment = file
            elif isinstance(file, SurveyDataSet):
                self._surveys.append(file)
            elif isinstance(file, ReferralDataSet):
                self._referrals.append(file)

    def get_appointments(self) -> list[AppointmentDataSet]:
        if not self._appointments:
            raise ValueError("Appointments not initialized")
        return self._appointments

    def get_enrollment(self) -> EnrollmentDataSet:
        if not self._enrollment:
            raise ValueError("Enrollment not initialized")
        return self._enrollment

    def get_survey_results(self) -> list[SurveyDataSet]:
        if not self._surveys:
            raise ValueError("Survey results not initialized")
        return self._surveys

    def get_referrals(self) -> list[ReferralDataSet]:
        if not self._referrals:
            raise ValueError("Referrals not initialized")
        return self._referrals

    def get_survey_by_id(self, survey_id) -> SurveyDataSet | None:
        for survey in self.get_survey_results():
            if survey.get_id() == survey_id:
                return survey
        return None

    # TODO: Allow for specification in config of what file(s) to load each report for (use list of files.config.json ids)
    def load_reports(self) -> list[Report] | None:
        if not self.config:
            return None

        self._reports = []

        reports = self.config["reports"]

        report_index = 0
        for report in reports:
            report_index += 1
            error = False
            if "type" not in report:
                logging.error(f"ERROR! \"type\" key not present in "
                              f"{self.config_file} at index {report_index}")
                error = True
            if "file_prefix" not in report:
                logging.error(f"ERROR! \"file_prefix\" key not present in "
                              f"{self.config_file} at index {report_index}")
                error = True
            if "results_dir" not in report:
                logging.error(f"ERROR! \"results_dir\" key not present in "
                              f"{self.config_file} at index {report_index}")
                error = True
            if error:
                logging.error(f"ERROR! Report {report_index} could not be "
                              f"loaded due to missing essential keys")
                break
            type = report["type"]
            if type == Report.Type.SURVEY_RESULTS.value:
                for appointment in self.get_appointments():
                    self.load_survey_results_report(report, report_index, appointment)

            if type == Report.Type.FOLLOWUP.value:
                for appointment in self.get_appointments():
                    self.load_followup_report(report, report_index, appointment)
            if type == Report.Type.REFERRALS.value:
                for referral in self.get_referrals():
                    for appointment in self.get_appointments():
                        self.load_referrals_report(report, report_index, referral, appointment)
        return self._reports

    def run_reports(self):
        if not self._reports:
            raise ValueError("Reports not initialized. \"load_reports()\" must be called first")
        for report in self._reports:
            if not isinstance(report, Report):
                raise ValueError("Reports must be of type Report")
            report.run_report()

            logging.info(f"Successfully ran {report.__class__.__name__} report")
            report.save_archive()
            logging.info(f"Saved archive of {report.__class__.__name__} report to {report.archive_dir}")
            report.save_results()
            logging.info(f"Saved results of {report.__class__.__name__} report to {report.results_dir}")

    def load_survey_results_report(self, report, report_index, appointment):
        if not self._reports:
            return
        if "survey_id" not in report:
            logging.error(
                f"ERROR! \"survey_id\" key not present for {type} "
                f"report in {self.config_file} at index "
                f"{report_index}")
            return

        survey_id = report["survey_id"]
        survey = self.get_survey_by_id(survey_id)
        if survey is None:
            logging.error(f"ERROR! No survey was found with the ID "
                          f"{survey_id}")
            return
        else:
            logging.info(f"Found survey with id {survey_id}")

        error = False
        if "day_range" not in report:
            logging.error(
                f"ERROR! \"day_range\" key not present for {type} "
                f"report in {self.config_file} at index "
                f"{report_index}")
            error = True
        if "target_year" not in report:
            report["target_year"] = None
            logging.warning(
                f"WARNING! \"target_year\" key not present for "
                f"{type} report in {self.config_file} at index "
                f"{report_index}. Setting to default including "
                f"all years")
        else:
            if report["target_year"] == "" or report["target_year"] == []:
                report["target_year"] = None
        if "target_months" not in report:
            logging.warning(
                f"WARNING! \"target_months\" key not present for {type} "
                f"in {self.config_file} at index {report_index}. "
                f"Setting to default including all months")
            report["target_months"] = None
        else:
            if report["target_months"] == "" or report["target_months"] == []:
                report["target_months"] = None

        if "emails" not in report:
            logging.warning(
                f"WARNING! \"emails\" key not present for {type} "
                f"in {self.config_file} at index {report_index}. "
                f"Setting to default including all emails")
            report["emails"] = None
        else:
            if report["emails"] == "" or report["emails"] == []:
                report["emails"] = None
        if error:
            logging.error(f"ERROR! Report {report_index} could not be "
                          f"loaded due to missing essential keys")
            return

        report_obj = SurveyResults(
            appointments=appointment.deep_copy(),
            survey_results=survey.deep_copy(),
            day_range=report["day_range"],
            target_years=report["target_years"],
            target_months=report["target_months"],
            staff_emails=FilterType(include=report["emails"]["include"], exclude=report["emails"]["exclude"]),
        )
        self._reports.append(Report(
            file_prefix=report["file_prefix"],
            archive_dir=report["archive_dir"],
            results_dir=report["results_dir"],
            report=report_obj,
            remove_cols=report["remove_cols"] + ['Time_Difference'] if "remove_cols" in report else ['Time_Difference'],
            rename_cols=report["rename_cols"] if "rename_cols" in report else None,
            final_cols=report["final_cols"] if "final_cols" in report else None
        ))

    def load_followup_report(self, report, report_index, appointment):
        if not self._reports:
            return

        error = False
        if "valid_schools" not in report:
            logging.warning(
                f"WARNING! \"valid_schools\" key not present for {type} report in {self.config_file} at index {report_index}. Setting to default including all schools")
            report["valid_schools"] = None
        else:
            if report["valid_schools"] == "" or report["valid_schools"] == []:
                report["valid_schools"] = None
        if "target_year" not in report:
            logging.warning(
                f"WARNING! \"target_year\" key not present for {type} report in {self.config_file} at index {report_index}. Setting to default including all years")
            report["target_year"] = None
        else:
            if report["target_year"] == "" or report["target_year"] == []:
                report["target_year"] = None
        if "target_months" not in report:
            logging.warning(
                f"WARNING! \"target_months\" key not present for {type} in {self.config_file} at index {report_index}. Setting to default including all months")
            report["target_months"] = None
        else:
            if report["target_months"] == "" or report["target_months"] == []:
                report["target_months"] = None
        if "appointment_types" not in report:
            logging.error(
                f"WARNING! \"appointment_types\" key not present for {type} in {self.config_file} at index {report_index}")
            error = True
        if "followup_types" not in report:
            logging.error(
                f"WARNING! \"followup_types\" key not present for {type} in {self.config_file} at index {report_index}")
            error = True
        if error:
            logging.error(f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
            return

        report_obj = Followup(
            appointments=appointment.deep_copy(),
            valid_schools=FilterType(include=report["valid_schools"]["include"], exclude=report["valid_schools"]["exclude"]),
            target_years=report["target_years"],
            target_months=report["target_months"],
            require_followup=FilterType(include=report["require_followup"]["include"], exclude=report["require_followup"]["exclude"]),
            followup_types=FilterType(include=report["followup_types"]["include"], exclude=report["followup_types"]["exclude"])
        )
        self._reports.append(Report(
            file_prefix=report["file_prefix"],
            archive_dir=report["archive_dir"],
            results_dir=report["results_dir"],
            report=report_obj,
            remove_cols=report["remove_cols"] if "remove_cols" in report else None,
            rename_cols=report["rename_cols"] if "rename_cols" in report else None,
            final_cols=report["final_cols"] if "final_cols" in report else None
        ))

    def load_referrals_report(self, report, report_index, referral, appointment):
        if not self._reports:
            return
        error = False
        if "valid_appointments" not in report:
            logging.error(
                f"ERROR! \"valid_appointments\" key not present for {type} report in {self.config_file} at index {report_index}")
            error = True
        if error:
            logging.error(
                f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
            return

        report_obj = Referrals(
            referrals=referral.deep_copy(),
            appointment=appointment.deep_copy(),
            complete_types=FilterType(include=report["valid_appointments"]["include"], exclude=report["valid_appointments"]["exclude"]),
            enrollment=self.get_enrollment().deep_copy(),
            merge_on=report["merge_enrollment"] if "merge_enrollment" in report else None
        )
        self._reports.append(Report(
            file_prefix=report["file_prefix"],
            archive_dir=report["archive_dir"],
            results_dir=report["results_dir"],
            report=report_obj,
            remove_cols=report["remove_cols"] if "remove_cols" in report else None,
            rename_cols=report["rename_cols"] if "rename_cols" in report else None,
            final_cols=report["final_cols"] if "final_cols" in report else None
        ))
