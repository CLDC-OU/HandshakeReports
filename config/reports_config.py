import json
import logging
from config.files_config import FilesConfig

from src.reports.followup import Followup
from src.reports.referrals import Referrals
from src.reports.report import Report
from src.dataset.appointment import AppointmentDataSet
from src.dataset.dataset import DataSet
from src.dataset.enrollment import EnrollmentDataSet
from src.dataset.referral import ReferralDataSet
from src.dataset.survey import SurveyDataSet
from src.reports.survey_results import SurveyResults

REPORTS_CONFIG_FILE = "reports.config.json"


class ReportsConfig:
    def __init__(self, config_file: str = REPORTS_CONFIG_FILE, files_config_file: str | None = None) -> None:
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
            self._files.load_files()
        self.load_files()

    def get_files(self) -> list[DataSet]:
        if not self._files:
            raise ValueError("FilesConfig not initialized")
        return self._files.files

    def get_reports(self) -> list[Report]:
        if not self._reports:
            raise ValueError("Reports not initialized")
        return self._reports

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
                    if "survey_id" not in report:
                        logging.error(
                            f"ERROR! \"survey_id\" key not present for {type} "
                            f"report in {self.config_file} at index "
                            f"{report_index}")
                        break

                    survey_id = report["survey_id"]
                    survey = self.get_survey_by_id(survey_id)
                    if survey is None:
                        logging.error(f"ERROR! No survey was found with the ID "
                                      f"{survey_id}")
                        break
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
                        break

                    # conf = {
                    #     "type": report["type"],
                    #     "file_prefix": report["file_prefix"],
                    #     "appointments": appointment.deep_copy(),
                    #     "survey_results": survey.deep_copy(),
                    #     "day_range": report["day_range"],
                    #     "year": report["target_year"],
                    #     "months": report["target_months"],
                    #     "emails": report["emails"],
                    #     "remove_cols": report["remove_cols"] if "remove_cols" in report else None,
                    #     "rename_cols": report["rename_cols"] if "rename_cols" in report else None,
                    #     "final_cols": report["final_cols"] if "final_cols" in report else None,
                    #     "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                    #     "results_dir": report["results_dir"] if "results_dir" in report else None
                    # }
                    report_obj = SurveyResults(
                        appointments=appointment.deep_copy(),
                        survey_results=survey.deep_copy(),
                        day_range=report["day_range"],
                        years=report["target_year"],
                        months=report["target_months"],
                        staff_emails=report["emails"],
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

            if type == Report.Type.FOLLOWUP.value:
                for appointment in self.get_appointments():
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
                        break
                    # conf = {
                    #     "type": report["type"],
                    #     "file_prefix": report["file_prefix"],
                    #     "appointments": appointment.deep_copy(),
                    #     "valid_schools": report["valid_schools"],
                    #     "year": report["target_year"],
                    #     "months": report["target_months"],
                    #     "appointment_types": report["appointment_types"],
                    #     "followup_types": report["followup_types"],
                    #     "remove_cols": report["remove_cols"] if "remove_cols" in report else None,
                    #     "rename_cols": report["rename_cols"] if "rename_cols" in report else None,
                    #     "final_cols": report["final_cols"] if "final_cols" in report else None,
                    #     "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                    #     "results_dir": report["results_dir"] if "results_dir" in report else None,
                    # }
                    report_obj = Followup(
                        appointments=appointment.deep_copy(),
                        valid_schools=report["valid_schools"],
                        years=report["target_year"],
                        months=report["target_months"],
                        require_followup=report["appointment_types"],
                        followup_types=report["followup_types"]
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
            if type == Report.Type.REFERRALS.value:
                for referral in self.get_referrals():
                    for appointment in self.get_appointments():
                        error = False
                        if "valid_appointments" not in report:
                            logging.error(
                                f"ERROR! \"valid_appointments\" key not present for {type} report in {self.config_file} at index {report_index}")
                            error = True
                        if error:
                            logging.error(
                                f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
                            break
                        # conf = {
                        #     "type": report["type"],
                        #     "file_prefix": report["file_prefix"],
                        #     "referrals": referral.deep_copy(),
                        #     "appointments": appointment.deep_copy(),
                        #     "valid_appointments": report["valid_appointments"],
                        #     "remove_cols": report["remove_cols"] if "remove_cols" in report else None,
                        #     "rename_cols": report["rename_cols"] if "rename_cols" in report else None,
                        #     "final_cols": report["final_cols"] if "final_cols" in report else None,
                        #     "enrollment": self.get_enrollment().deep_copy(),
                        #     "merge_enrollment": report["merge_enrollment"] if "merge_enrollment" in report else None,
                        #     "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                        #     "results_dir": report["results_dir"] if "results_dir" in report else None,
                        # }
                        report_obj = Referrals(
                            referrals=referral.deep_copy(),
                            appointment=appointment.deep_copy(),
                            valid_appointment_pattern=report["valid_appointments"],
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
