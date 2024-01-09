from enum import Enum
import logging

import pandas as pd
from src.reports.followup import Followup
from src.reports.referrals import Referrals
from src.reports.survey_results import SurveyResults
from src.utils.df_utils import remove_columns
from datetime import datetime as dt


class Report:
    class Type(Enum):
        SURVEY_RESULTS = 'survey_results'
        FOLLOWUP = 'followup'
        REFERRALS = 'referrals'

        def __eq__(self, __value: object) -> bool:
            return self.value.__eq__(__value)

    def __init__(
            self,
            file_prefix: str,
            results_dir: str,
            report: SurveyResults | Followup | Referrals,
            archive_dir: str | None = None,
            remove_cols: list[str] | None = None,
            rename_cols: dict | None = None,
            final_cols: list[str] | None = None
    ) -> None:
        self.file_prefix = file_prefix
        self.results_dir = results_dir
        self.report = report
        self.archive_dir = archive_dir
        self.remove_cols = remove_cols
        self.rename_cols = rename_cols
        self.final_cols = final_cols
        self.results = None

    def run_report(self) -> None:
        logging.debug(f"Running report for {self.__class__.__name__}")
        self.report.run_report()
        self.results = self.report.get_results()

    @property
    def results(self) -> pd.DataFrame | None:
        if not isinstance(self.results, pd.DataFrame):
            logging.warning(f"Invalid results type {type(self.results)}. Using None")
            return None
        return self.results

    @results.setter
    def results(self, value: pd.DataFrame | None) -> None:
        self.results = value

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
