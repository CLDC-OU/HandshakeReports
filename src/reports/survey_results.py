import logging
import pandas as pd
from src.dataset.appointment import AppointmentDataSet
from src.dataset.survey import SurveyDataSet
from src.utils.df_utils import filter_by_time_diff
from src.reports.report import Report
from src.utils.type_utils import FilterType


class SurveyResults(Report):
    def __init__(self, appointments: AppointmentDataSet, survey_results: SurveyDataSet, day_range: int, target_years: str | None, target_months: str | None, staff_emails: FilterType) -> None:
        if not isinstance(appointments, AppointmentDataSet) or not isinstance(survey_results, SurveyDataSet):
            raise ValueError('Invalid DataSet types provided at filter_appointment_surveys')
        self.appointments = appointments
        self.survey_results = survey_results
        self.results = pd.DataFrame(None)
        self.day_range = day_range
        self.years = target_years
        self.months = target_months
        self.staff_emails = staff_emails

    def run_report(self) -> None:
        self.appointments.sort_date()
        logging.debug("Sorted appointments by date")
        self.survey_results.sort_date()
        logging.debug("Sorted survey results by date")

        self.appointments.filter_appointment_status()
        logging.debug("Filtered valid appointment statuses")
        if self.years is not None:
            self.appointments.filter_years(*self.years.split(','))
            logging.debug("Filtered years")
        if self.months is not None:
            self.appointments.filter_months(*self.months.split(','))
            logging.debug("Filtered months")
        if self.staff_emails is not None:
            self.appointments.filter_staff_emails(self.staff_emails)
            logging.debug("Filtered staff emails")

        self._normalize_email_cols()
        self.results = self._filter_by_time_diff()
        logging.debug("Filtered time difference")

    def get_results(self) -> pd.DataFrame | None:
        return self.results

    # ensure the student email columns have the same name. Rename the survey set to match
    def _normalize_email_cols(self) -> None:
        if self.survey_results.get_col_name(SurveyDataSet.Column.STUDENT_EMAIL) != self.appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL):
            self.survey_results.get_df().rename(
                {self.survey_results.get_col_name(SurveyDataSet.Column.STUDENT_EMAIL): self.appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)}
            )

    def _filter_by_time_diff(self) -> pd.DataFrame:
        date_col_1 = self.survey_results.get_col_name(SurveyDataSet.Column.DATE)
        date_col_2 = self.appointments.get_col_name(AppointmentDataSet.Column.DATE)
        merge_col = self.appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        if not date_col_1 or not date_col_2 or not merge_col:
            raise ValueError("One or more columns are not defined")

        return filter_by_time_diff(
            df_1=self.survey_results.get_df(),
            col_1=date_col_1,
            df_2=self.appointments.get_df(),
            col_2=date_col_2,
            days=self.day_range,
            merge_col=merge_col,
        )

    @property
    def day_range(self) -> int:
        return self._day_range

    @day_range.setter
    def day_range(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("day_range must be an integer greater than or equal to 0")
        self._day_range = value

    @property
    def years(self) -> str | None:
        return self._years

    @years.setter
    def years(self, value: str | None) -> None:
        if not isinstance(value, str) and value is not None:
            raise ValueError("years must be a string or None")
        self._years = value

    @property
    def months(self) -> str | None:
        return self._months

    @months.setter
    def months(self, value: str | None) -> None:
        if not isinstance(value, str) and value is not None:
            raise ValueError("months must be a string or None")
        self._months = value

    @property
    def staff_emails(self) -> FilterType:
        return self._staff_emails

    @staff_emails.setter
    def staff_emails(self, value: FilterType) -> None:
        if not isinstance(value, FilterType):
            raise ValueError("staff_emails must be a FilterType")
        self._staff_emails = value

    @property
    def appointments(self) -> AppointmentDataSet:
        return self._appointments

    @appointments.setter
    def appointments(self, value: AppointmentDataSet) -> None:
        if not isinstance(value, AppointmentDataSet):
            raise ValueError("appointments must be an AppointmentDataSet")
        self._appointments = value
        logging.debug("Appointments updated")

    @property
    def survey_results(self) -> SurveyDataSet:
        return self._survey_results

    @survey_results.setter
    def survey_results(self, value: SurveyDataSet) -> None:
        if not isinstance(value, SurveyDataSet):
            raise ValueError("survey_results must be a SurveyDataSet")
        self._survey_results = value
        logging.debug("Survey results updated")

    @property
    def results(self) -> pd.DataFrame:
        return self._results

    @results.setter
    def results(self, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise ValueError("results must be a DataFrame")
        self._results = value
        logging.debug("Results updated")
