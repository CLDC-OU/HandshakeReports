import logging
import pandas as pd
from src.dataset.appointment import AppointmentDataSet
from src.dataset.dataset import DataSet
from src.dataset.dataset import Column
from src.dataset.survey import SurveyDataSet
from src.utils.df_utils import filter_by_time_diff
from src.reports.report import Report
from src.utils.type_utils import FilterType


class SurveyResults(Report):
    def __init__(self, appointments: DataSet, survey_results: DataSet, day_range: int, target_years: str | None, target_months: str | None, staff_emails: FilterType) -> None:
        if not isinstance(appointments, AppointmentDataSet) or not isinstance(survey_results, SurveyDataSet):
            raise ValueError('Invalid DataSet types provided at filter_appointment_surveys')
        self._appointments = appointments
        self._survey_results = survey_results
        self.results = None
        self._day_range = day_range
        self._years = target_years
        self._months = target_months
        self._staff_emails = staff_emails

    def run_report(self) -> None:
        self._appointments.sort_date()
        logging.debug("Sorted appointments by date")
        self._survey_results.sort_date()
        logging.debug("Sorted survey results by date")

        self._appointments.filter_appointment_status()
        logging.debug("Filtered valid appointment statuses")
        if self._years is not None:
            self._appointments.filter_years(*self._years.split(','))
            logging.debug("Filtered years")
        if self._months is not None:
            self._appointments.filter_months(*self._months.split(','))
            logging.debug("Filtered months")
        if self._staff_emails is not None:
            self._appointments.filter_staff_emails(self._staff_emails)
            logging.debug("Filtered staff emails")

        self._normalize_email_cols()
        self.results = self._filter_by_time_diff()
        logging.debug("Filtered time difference")

    def get_results(self) -> pd.DataFrame | None:
        return self.results

    # ensure the student email columns have the same name. Rename the survey set to match
    def _normalize_email_cols(self) -> None:
        if self._survey_results.get_col_name(Column.STUDENT_EMAIL) != self._appointments.get_col_name(Column.STUDENT_EMAIL):
            self._survey_results.get_df().rename(
                {self._survey_results.get_col_name(Column.STUDENT_EMAIL): self._appointments.get_col_name(Column.STUDENT_EMAIL)}
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
