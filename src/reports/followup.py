import logging
import pandas as pd
from src.dataset.dataset import Column, DataSet
from src.reports.report import Report
from utils.type_utils import FilterType


class Followup(Report):
    def __init__(self, appointments: DataSet, valid_schools: FilterType, target_years: str | None, target_months: str | None,
                 require_followup: FilterType, followup_types: FilterType) -> None:
        if not isinstance(valid_schools, FilterType):
            raise ValueError("valid_schools must be a FilterType")
        if not isinstance(require_followup, FilterType):
            raise ValueError("require_followup must be a FilterType")
        if not isinstance(followup_types, FilterType):
            raise ValueError("followup_types must be a FilterType")
        self._appointments = appointments
        self._results = None
        self._valid_schools = valid_schools
        self._years = target_years
        self._months = target_months
        self._require_followup = require_followup
        self._latest_followup_col = 'date of last followup appointment'
        self.followup_types = followup_types

    def run_report(self):
        self._filter_year()
        logging.debug("Filtered appointment year")
        self._filter_months()
        logging.debug("Filtered appointment months")
        self._filter_schools()
        logging.debug("Filtered student schools")
        self._get_all_need_followup()
        logging.debug(f"Filtered students that need a followup {self._latest_followup_col} appointment")
        self._add_latest_followup()
        logging.debug("Added latest followup column")
        self._remove_followed_up()
        logging.debug("Removed rows that already had a followup appointment")
        self._keep_max_date()
        logging.debug("Removed rows where student had a more recent appointment")
        self._add_past_followup_count()
        logging.debug("Added previous followup appointment count")

    def get_results(self):
        return self._results

    def _filter_year(self):
        if not self._years:
            return
        self._appointments.filter_years(*self._years.split(','))

    def _filter_months(self):
        if not self._months:
            return
        self._appointments.filter_months(*self._months.split(','))

    def _filter_schools(self):
        # print(self._valid_schools)
        self._appointments.filter_schools(self._valid_schools)

    def _get_all_need_followup(self):
        app_type_col = self._appointments.get_col_name(Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')
        self._results = self._appointments.get_df()[
            self._appointments.get_df()[app_type_col].str.startswith(self._appointment_types["include"])
            & ~(self._appointments.get_df()[app_type_col].isin(self._appointment_types["disclude"]))
            ]
        # print(self._appointment_types["include"])
        # print(self._appointment_types["disclude"])

    def _remove_followed_up(self):
        date_col = self._appointments.get_col_name(Column.DATE)

        # keep only rows where the latest followup appointment is before the latest needs followup, or the student
        # has never had a valid followup appointment
        self._results = self._results[(
                (self._results[date_col].notna())
                & (
                        (self._results[self._latest_followup_col].isna())
                        | (self._results[date_col] >= self._results[self._latest_followup_col])
                )
        )]

    def _keep_max_date(self):
        date_col = self._appointments.get_col_name(Column.DATE)
        email_col = self._appointments.get_col_name(Column.STUDENT_EMAIL)
        self._results = self._results.loc[self._results.groupby(email_col)[date_col].idxmax()]

    def _get_latest_valid_followup_dates(self) -> pd.DataFrame:
        email_col = self._appointments.get_col_name(Column.STUDENT_EMAIL)
        date_col = self._appointments.get_col_name(Column.DATE)
        valid_followup = self._get_followup_appointments()
        logging.debug("got valid followup appointments")
        return valid_followup.groupby(email_col)[date_col].max().reset_index(
            name=self._latest_followup_col
        )

    def _add_latest_followup(self):
        email_col = self._appointments.get_col_name(Column.STUDENT_EMAIL)
        self._results = pd.merge(
            left=self._results,
            right=self._get_latest_valid_followup_dates(),
            on=email_col,
            how='left'
        )

    def _add_past_followup_count(self):
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)

        col_name = f'# of past non {self._appointment_types["include"]} appointments'

        duplicate_appointment_count = self._get_followup_appointments().pivot_table(
            index=[email_col],
            aggfunc='size'
        ).reset_index(col_fill=col_name)

        self._results = pd.merge(
            left=self._results,
            right=duplicate_appointment_count,
            how="left",
            on=email_col
        )

    def _get_followup_appointments(self) -> pd.DataFrame:
        app_type_col = self._appointments.get_col(Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')
        return self._appointments.get_df()[
            ~(self._appointments.get_df()[app_type_col].str.startswith(self._appointment_types["include"]))
            | (self._appointments.get_df()[app_type_col].isin(self._appointment_types["disclude"]))
            ]
