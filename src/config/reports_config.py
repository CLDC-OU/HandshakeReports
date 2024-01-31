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
            logging.debug(f"Loading reports config from {config_file}")
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
            message = "ERROR! No reports config initialized. Cannot load reports"
            logging.error(message)
            print(message)
            return None

        self._reports = []

        reports = self.config["reports"]

        message = f"Loading {len(reports)} reports from {self.config_file}"
        logging.info(message)
        print(message)

        report_index = 0
        for report in reports:
            report_index += 1
            # TODO: Refactor this to use a function for key checking
            required_keys = ["type", "file_prefix", "results_dir"]

            if not self.validate_keys(
                required_keys=required_keys,
                warning_keys=[],
                report=report,
                report_index=report_index
            ):
                message = f"\tERROR! Report {report_index} could not be loaded due to missing essential keys"
                logging.error(message)
                print(message)
                break

            message = f"\tLoading {report['type']} report from {self.config_file} at index {report_index}"
            logging.debug(message)
            print(message)
            if report["type"] == "survey_results":
                for appointment in self.get_appointments():
                    self.load_survey_results_report(report, report_index, appointment)
            elif report["type"] == "followup":
                for appointment in self.get_appointments():
                    self.load_followup_report(report, report_index, appointment)
            elif report["type"] == "referrals":
                for referral in self.get_referrals():
                    for appointment in self.get_appointments():
                        self.load_referrals_report(report, report_index, referral, appointment)
            else:
                message = f"\tWARNING: Report {report_index} could not be loaded. Invalid type {report['type']}. This report will be skipped"
                logging.error(message)
                print(message)
                continue
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

    def load_survey_results_report(self, report: dict, report_index: int, appointment: AppointmentDataSet):
        if not isinstance(self._reports, list):
            raise ValueError("Reports must be a list. Reports may not have been initialized. \"load_reports()\" must be called first")
        # TODO: Refactor this to use a function for key checking
        if not self.validate_keys(
            required_keys=["survey_id", "day_range"],
            warning_keys=["target_date_ranges" "emails"],
            report=report,
            report_index=report_index,
            report_type="SurveyResults"
        ):
            return

        survey_id = report["survey_id"]
        survey = self.get_survey_by_id(survey_id)
        if survey is None:
            logging.error(f"ERROR! No survey was found with the ID "
                          f"{survey_id}")
            return
        else:
            logging.info(f"Found survey with id {survey_id}")

        report_obj = SurveyResults(
            appointments=appointment.deep_copy(),
            survey_results=survey.deep_copy(),
            day_range=report["day_range"],
            target_date_ranges=report["target_date_ranges"],
            staff_emails=FilterType.get_include_exclude(
                dictionary=report,
                key="emails",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="SurveyResults"
            ),
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
        message = f"\t\tLoaded {report_obj.__class__.__name__} report from {self.config_file} at index {report_index}"
        print(message)
        logging.info(message)

    def load_followup_report(self, report: dict, report_index: int, appointment: AppointmentDataSet):
        if not isinstance(self._reports, list):
            raise ValueError("Reports must be a list. Reports may not have been initialized. \"load_reports()\" must be called first")

        # TODO: Refactor this to use a function for key checking

        if not self.validate_keys(
            required_keys=["require_followup"],
            warning_keys=["target_date_ranges", "valid_schools", "followup_types"],
            report=report,
            report_index=report_index,
            report_type="Followup"
        ):
            return

        report_obj = Followup(
            appointments=appointment.deep_copy(),
            valid_schools=FilterType.get_include_exclude(
                dictionary=report,
                key="valid_schools",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="Followup"
            ),
            target_date_ranges=report["target_date_ranges"],
            require_followup=FilterType.get_include_exclude(
                dictionary=report,
                key="require_followup",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="Followup"
            ),
            followup_types=FilterType.get_include_exclude(
                dictionary=report,
                key="followup_types",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="Followup"
            )
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
        message = f"\t\tLoaded {report_obj.__class__.__name__} report from {self.config_file} at index {report_index}"
        print(message)
        logging.info(message)

    def load_referrals_report(self, report: dict, report_index: int, referral: ReferralDataSet, appointment: AppointmentDataSet):
        if not isinstance(self._reports, list):
            raise ValueError("Reports must be a list. Reports may not have been initialized. \"load_reports()\" must be called first")
        # TODO: Refactor this to use a function for key checking
        if not self.validate_keys(
            required_keys=[],
            warning_keys=["valid_appointments", "merge_enrollment", "valid_department"],
            report=report,
            report_index=report_index,
            report_type="Referrals"
        ):
            return

        report_obj = Referrals(
            referrals=referral.deep_copy(),
            appointment=appointment.deep_copy(),
            valid_departments=FilterType.get_include_exclude(
                dictionary=report,
                key="valid_departments",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="Referrals"
            ),
            complete_types=FilterType.get_include_exclude(
                dictionary=report,
                key="valid_appointments",
                log=True,
                config_file=self.config_file,
                report_index=report_index,
                report_type="Referrals"
            ),
            enrollment=self.get_enrollment().deep_copy(),
            merge_on=report["merge_enrollment"]
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
        message = f"\t\tLoaded {report_obj.__class__.__name__} report from {self.config_file} at index {report_index}"
        print(message)
        logging.info(message)

    @staticmethod
    def validate_key(dictionary: dict, key: str, required: bool, report_type: str, config_file: str, report_index: int) -> bool:
        if key not in dictionary:
            if required:
                logging.error(
                    f"ERROR! \"{key}\" key not present for {report_type} report in {config_file} at index {report_index}.")
                return False
            else:
                logging.warning(
                    f"WARNING! \"{key}\" key not present for {report_type} report in {config_file} at index {report_index}. Setting to default including all {key}")
            dictionary[key] = None
        if dictionary[key] == "" or dictionary[key] == []:
            dictionary[key] = None
        return True

    def validate_keys(self, required_keys: list, warning_keys: list, report: dict, report_index: int, report_type: str = "Report") -> bool:
        error = False
        for key in required_keys:
            if not ReportsConfig.validate_key(
                    dictionary=report,
                    key=key,
                    required=True,
                    report_type=report_type,
                    config_file=self.config_file,
                    report_index=report_index
            ):
                error = True
        for key in warning_keys:
            ReportsConfig.validate_key(
                dictionary=report,
                key=key,
                required=False,
                report_type=report_type,
                config_file=self.config_file,
                report_index=report_index
            )

        if error:
            logging.error(f"ERROR! Report {report_index} could not be "
                          f"loaded due to missing essential keys")
            return False
        return True
