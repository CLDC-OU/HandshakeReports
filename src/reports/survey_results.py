import logging
import pandas as pd
from .DataSet import Column, DataSet
from Utils.df_utils import filter_by_time_diff
from datetime import datetime as dt


class SurveyResults():
    def __init__(self, appointments: DataSet, survey_results: DataSet, day_range: int, year: str | None, months: list | None, emails: list | None, remove_cols: list) -> None:
        if appointments.get_type() != DataSet.Type.APPOINTMENT or survey_results.get_type() != DataSet.Type.SURVEY:
            logging.error(f'Invalid DataSet types provided at filter_appointment_surveys')
            return False
        self._appointments = appointments
        self._survey_results = survey_results
        self._results = None
        self._day_range = day_range
        self._year = year
        self._months = months
        self._emails = emails
        if not remove_cols:
            self.remove_cols = ['Time_Difference']
        else:
            self.remove_cols = remove_cols + ['Time_Difference']
        self.rename_cols = None
        self.final_cols = None

    def run_report(self) -> None:
        self._appointments.sort_date()
        logging.debug(f"Sorted appointments by date")
        self._survey_results.sort_date()
        logging.debug(f"Sorted survey results by date")

        self._appointments.filter_appointment_status()
        logging.debug(f"Filtered valid appointment statuses")
        if self._year is not None:
            self._appointments.filter_year(self._year)
            logging.debug(f"Filtered year")
        if self._months is not None:
            self._appointments.filter_months(self._months)
            logging.debug(f"Filtered months")
        if self._emails is not None:
            self._appointments.filter_staff_emails(self._emails)
            logging.debug(f"Filtered staff emails")

        self._normalize_email_cols()
        self._results = self._filter_by_time_diff()
        logging.debug(f"Filtered time difference")

    def get_results(self) -> pd.DataFrame | None:
        return self._results

    # ensure the student email columns have the same name. Rename the survey set to match
    def _normalize_email_cols(self) -> None:
        if self._survey_results.get_col(Column.STUDENT_EMAIL) != self._appointments.get_col(Column.STUDENT_EMAIL):
            self._survey_results.get_df().rename(
                {self._survey_results.get_col(Column.STUDENT_EMAIL): self._appointments.get_col(Column.STUDENT_EMAIL)}
            )

    def _filter_by_time_diff(self) -> pd.DataFrame:
        return filter_by_time_diff(
            df_1=self._survey_results.get_df(),
            col_1=self._survey_results.get_col(Column.DATE),
            df_2=self._appointments.get_df(),
            col_2=self._appointments.get_col(Column.DATE),
            days=self._day_range,
            merge_col=self._appointments.get_col(Column.STUDENT_EMAIL),
        )
