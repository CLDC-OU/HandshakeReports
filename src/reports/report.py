from enum import Enum
import logging

import pandas as pd
from .Followup import Followup
from .Referrals import Referrals
from .SurveyResults import SurveyResults
from Utils.df_utils import remove_columns
from datetime import datetime as dt


class Report:
    class Type(Enum):
        SURVEY_RESULTS = 'survey_results'
        FOLLOWUP = 'followup'
        REFERRALS = 'referrals'

        def __eq__(self, __value: object) -> bool:
            return self.value.__eq__(__value)

    def __init__(self, config: dict) -> None:
        self.type = config["type"]
        self.file_prefix = config["file_prefix"]
        self.archive_dir = config["archive_dir"]
        self.results_dir = config["results_dir"]
        if config["type"] == Report.Type.SURVEY_RESULTS:
            logging.debug(f"Creating new SurveyResults Report")
            self.report = SurveyResults(
                appointments=config["appointments"],
                survey_results=config["survey_results"],
                day_range=config["day_range"],
                year=config["year"],
                months=config["months"],
                emails=config["emails"],
                remove_cols=config["remove_cols"]
            )
            self.results = None
        elif config["type"] == Report.Type.FOLLOWUP:
            logging.debug(f"Creating new Followup Report")
            self.report = Followup(
                appointments=config["appointments"],
                valid_schools=config["valid_schools"],
                year=config["year"],
                months=config["months"],
                appointment_types=config["appointment_types"],
                followup_types=config["followup_types"],
                remove_cols=config["remove_cols"],
                rename_cols=config["rename_cols"],
                final_cols=config["final_cols"]
            )
            self.results = None
        elif config["type"] == Report.Type.REFERRALS:
            logging.debug(f"Creating new Referrals Report")
            self.report = Referrals(
                referrals=config["referrals"],
                appointment=config["appointments"],
                valid_appointment_pattern=config["valid_appointments"],
                rename_cols=config["rename_cols"],
                final_cols=config["final_cols"],
                enrollment=config["enrollment"],
                merge_on=config["merge_enrollment"]
            )
            self.results = None
        else:
            logging.error(f"Invalid Report Type {config['type']}")
            self.report = None
            self.results = pd.DataFrame(None)

    def run_report(self) -> None:
        logging.debug(f"Running report for {self.type}")
        self.report.run_report()
        self.results = self.report.get_results()

    def get_results(self) -> pd.DataFrame | None:
        return self.results

    def get_filename(self) -> str:
        return self.file_prefix + dt.now().strftime('%Y%m%d-%H%M%S') + '.csv'

    def save_archive(self):
        self.results.to_csv(self.archive_dir + "\\" + self.get_filename(), index=False)

    def save_results(self):
        if self.results.empty:
            return None

        if self.report.remove_cols:
            self.results = remove_columns(self.results, self.report.remove_cols)
        if self.report.rename_cols:
            # print(self.report.rename_cols)
            self.results = self.results.rename(columns=self.report.rename_cols)
        if self.report.final_cols:
            self.results = self.results[self.report.final_cols]

        self.results.to_csv(self.results_dir + "\\" + self.get_filename())

    # def __init__(self, type, report:SurveyResults|Followup) -> None:
    #     self.type = type
    #     self.report = report
    # def __init_subclass__(cls, config) -> None:
    #     cls.type = config["type"]
    #     if config["type"] == ReportType.SURVEY_RESULTS:
    #         cls.report = SurveyResults(config["file_prefix"], config["appointments"], config["survey_results"], config["target_year"], config["target_months"], config["emails"], config["remove_cols"])
    #     elif config["type"] == ReportType.FOLLOWUP:
    #         cls.report = Followup(config["file_prefix"], config["appointments"], config["valid_majors"], config["target_year"], config["target_months"], config["remove_cols"], config["rename_cols"], config["final_cols"])
    #     else:
    #         cls.report = None
