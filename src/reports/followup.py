import logging
import pandas as pd
from src.dataset.appointment import AppointmentDataSet
from src.reports.report import Report
from src.utils.general_utils import get_date_ranges
from src.utils.type_utils import FilterType


class Followup(Report):
    def __init__(self, appointments: AppointmentDataSet, valid_schools: FilterType, target_date_ranges: str | None,
                 require_followup: FilterType, followup_types: FilterType) -> None:
        if not isinstance(valid_schools, FilterType):
            raise ValueError("valid_schools must be a FilterType")
        if not isinstance(require_followup, FilterType):
            raise ValueError("require_followup must be a FilterType")
        if not isinstance(followup_types, FilterType):
            raise ValueError("followup_types must be a FilterType")
        self._appointments = appointments
        self.results = None
        self._valid_schools = valid_schools
        self.target_date_ranges = target_date_ranges
        self._require_followup = require_followup
        self._latest_followup_col = 'date of last followup appointment'
        self.followup_types = followup_types

    def run_report(self):
        self._filter_target_date_ranges()
        logging.debug(f"Filtered appointments for target date ranges: {self.target_date_ranges}")
        self._filter_schools()
        logging.debug(f"Filtered student schools: {self._valid_schools}")
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
        return self.results

    def _filter_target_date_ranges(self):
        if self.target_date_ranges is not None:
            self._appointments.filter_dates(*get_date_ranges(self.target_date_ranges))

    def _filter_schools(self):
        self._appointments.filter_schools(self._valid_schools)

    def _get_all_need_followup(self):
        app_type_col = self._appointments.get_col_name(AppointmentDataSet.Column.APPOINTMENT_TYPE)
        if not app_type_col:
            raise ValueError("Appointment type column is not defined")
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')

        self.results = self._appointments.get_df()[
            self._appointments.get_df()[app_type_col].str.contains(
                self._require_followup.get_include()
            ) & ~(
                self._appointments.get_df()[app_type_col].str.contains(
                    self._require_followup.get_exclude()
                )
            )
        ]

    def _remove_followed_up(self):
        date_col = self._appointments.get_col_name(AppointmentDataSet.Column.DATE)

        if self.results is None or self.results.empty:
            raise ValueError("Results are undefined. Is the script running in the correct order?")

        # keep only rows where the latest followup appointment is before the latest needs followup, or the student
        # has never had a valid followup appointment
        self.results = self.results[(
            (self.results[date_col].notna()) & (
                (self.results[self._latest_followup_col].isna()) | (
                    self.results[date_col] >= self.results[self._latest_followup_col])
            )
        )]

    def _keep_max_date(self):
        date_col = self._appointments.get_col_name(AppointmentDataSet.Column.DATE)
        email_col = self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        if not date_col or not email_col:
            raise ValueError("Date or email column is not defined")
        if self.results is None or self.results.empty:
            raise ValueError("Results are undefined. Is the script running in the correct order?")
        self.results = self.results.loc[self.results.groupby(by=email_col)[date_col].idxmax()]

    def _get_latest_valid_followup_dates(self) -> pd.DataFrame:
        email_col = self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        date_col = self._appointments.get_col_name(AppointmentDataSet.Column.DATE)
        if not email_col or not date_col:
            raise ValueError("Email or date column is not defined")
        valid_followup = self._get_followup_appointments()
        logging.debug("got valid followup appointments")
        return valid_followup.groupby(by=email_col)[date_col].max().reset_index(
            name=self._latest_followup_col
        )

    def _add_latest_followup(self):
        email_col = self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        if self.results is None or self.results.empty:
            raise ValueError("Results are undefined. Is the script running in the correct order?")
        self.results = pd.merge(
            left=self.results,
            right=self._get_latest_valid_followup_dates(),
            on=email_col,
            how='left'
        )

    def _add_past_followup_count(self):
        email_col = self._appointments.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)

        col_name = '# of past followup appointments'

        duplicate_appointment_count = self._get_followup_appointments().pivot_table(
            index=[email_col],
            aggfunc='size'
        ).reset_index().rename(columns={0: col_name})

        if self.results is None or self.results.empty:
            raise ValueError("Results are undefined. Is the script running in the correct order?")

        self.results = pd.merge(
            left=self.results,
            right=duplicate_appointment_count,
            how="left",
            on=email_col
        )

    # TODO: this should implement the logic of dataset.py's filter_by_col. A new function for this should be made in dataset.py
    def _get_followup_appointments(self) -> pd.DataFrame:
        if not self.followup_types:
            return self._appointments.get_df()[
                ~(
                    self._appointments.get_col(AppointmentDataSet.Column.APPOINTMENT_TYPE).str.contains(
                        self._require_followup.get_include()
                    )
                ) | (
                    self._appointments.get_col(AppointmentDataSet.Column.APPOINTMENT_TYPE).str.contains(
                        self._require_followup.get_exclude()
                    )
                )
            ]
        app_type_col = self._appointments.get_col_name(AppointmentDataSet.Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_col(AppointmentDataSet.Column.APPOINTMENT_TYPE).fillna('MissingData')
        return self._appointments.get_df()[
            self._appointments.get_col(AppointmentDataSet.Column.APPOINTMENT_TYPE).str.contains(
                self.followup_types.get_include()
            ) & ~(
                self._appointments.get_col(AppointmentDataSet.Column.APPOINTMENT_TYPE).str.contains(
                    self.followup_types.get_exclude()
                )
            )
        ]
