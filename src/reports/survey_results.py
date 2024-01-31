import logging
import pandas as pd
from src.dataset.appointment import AppointmentDataSet
from src.dataset.survey import SurveyDataSet
from src.utils.df_utils import filter_by_time_diff
from src.reports.report import Report
from src.utils.general_utils import get_date_ranges
from src.utils.type_utils import FilterType


class SurveyResults(Report):
    def __init__(self, appointments: AppointmentDataSet, survey_results: SurveyDataSet, day_range: int, target_dates: str | None, staff_emails: FilterType) -> None:
        if not isinstance(appointments, AppointmentDataSet) or not isinstance(survey_results, SurveyDataSet):
            raise ValueError('Invalid DataSet types provided at filter_appointment_surveys')
        self._appointments = appointments
        self._survey_results = survey_results
        self.results = None
        self._day_range = day_range
        self.target_dates = target_dates
        self._staff_emails = staff_emails

    def run_report(self) -> None:
        self._appointments.sort_date()
        logging.debug("Sorted appointments by date")
        self._survey_results.sort_date()
        logging.debug("Sorted survey results by date")

        self._appointments.filter_appointment_status()
        logging.debug("Filtered valid appointment statuses")
        if self.target_dates is not None:
            self._appointments.filter_dates(*get_date_ranges(self.target_dates))
            logging.debug("Filtered target dates")
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
        if self._survey_results.get_col_name(SurveyDataSet.Column.STUDENT_EMAIL) != self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL):
            self._survey_results.get_df().rename(
                {self._survey_results.get_col_name(SurveyDataSet.Column.STUDENT_EMAIL): self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)}
            )

    def _filter_by_time_diff(self) -> pd.DataFrame:
        date_col_1 = self._survey_results.get_col_name(SurveyDataSet.Column.DATE)
        date_col_2 = self._appointments.get_col_name(AppointmentDataSet.Column.DATE)
        merge_col = self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        if not date_col_1 or not date_col_2 or not merge_col:
            raise ValueError("One or more columns are not defined")

        return filter_by_time_diff(
            df_1=self._survey_results.get_df(),
            col_1=date_col_1,
            df_2=self._appointments.get_df(),
            col_2=date_col_2,
            days=self._day_range,
            merge_col=merge_col,
        )
