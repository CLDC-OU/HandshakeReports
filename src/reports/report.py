from enum import Enum
import logging

import pandas as pd

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
            report: "Report",
            archive_dir: str | None = None,
            remove_cols: list[str] | None = None,
            rename_cols: dict | None = None,
            final_cols: list[str] | None = None
    ) -> None:
        self.file_prefix = file_prefix
        if not results_dir:
            raise ValueError("results_dir must be a valid directory")
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

    @property
    def rename_cols(self) -> dict[str, str] | None:
        if not isinstance(self.rename_cols, dict):
            logging.warning(f"Invalid rename_cols type {type(self.rename_cols)}. Using None")
            return None
        return self.rename_cols

    @rename_cols.setter
    def rename_cols(self, value: dict[str, str] | None) -> None:
        if not isinstance(self.rename_cols, dict):
            logging.warning(f"Invalid rename_cols type {type(value)}. Using None")
            self.rename_cols = None
        self.rename_cols = value

    def get_filename(self) -> str:
        return self.file_prefix + dt.now().strftime('%Y%m%d-%H%M%S') + '.csv'

    def save_archive(self):
        if not self.archive_dir:
            logging.debug("No archive directory specified. Skipping archive")
            return
        if not self.results or self.results.empty:
            raise ValueError("No results to archive")
        self.results.to_csv(self.archive_dir + "\\" + self.get_filename(), index=False)

    def save_results(self):
        if not self.results or self.results.empty:
            raise ValueError("No results to save")

        if self.remove_cols:
            self.results = remove_columns(self.results, self.remove_cols)
        if self.rename_cols:
            self.results = self.results.rename(columns=self.rename_cols)
        if self.final_cols:
            self.results = self.results[self.final_cols]

        self.results.to_csv(self.results_dir + "\\" + self.get_filename())
