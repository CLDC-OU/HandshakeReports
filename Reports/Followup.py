import logging
import pandas as pd
from .DataSet import Column, DataSet


class Followup:
    def __init__(self, appointments: DataSet, valid_schools: list | None, year: str | None, months: list | None,
                 appointment_types: list, followup_types: list, remove_cols=None, rename_cols=None,
                 final_cols=None) -> None:
        self._appointments = appointments
        self._results = None
        self._valid_schools = valid_schools
        self._year = year
        self._months = months
        if appointment_types:
            self._appointment_types = appointment_types
            include = self._appointment_types[self._appointment_types.index("include")]
            self._latest_followup_col = f'date of last non {include} appointment'
        else:
            # raise ValueError
            self._appointment_types = None
            self._latest_followup_col = None
        if followup_types:
            self.followup_types = followup_types
        else:
            self.followup_types = None
        self.remove_cols = remove_cols
        self.rename_cols = rename_cols
        self.final_cols = final_cols

    def run_report(self):
        if self._year is not None:
            self._filter_year()
            logging.debug(f"Filtered appointment year")
        if self._months is not None:
            self._filter_months()
            logging.debug(f"Filtered appointment months")
        if self._valid_schools is not None:
            self._filter_schools()
            logging.debug(f"Filtered student schools")
        self._get_all_need_followup()
        logging.debug(f"Filtered students that need a followup {self._latest_followup_col} appointment")
        self._add_latest_followup()
        logging.debug(f"Added latest followup column")
        self._remove_followed_up()
        logging.debug(f"Removed rows that already had a followup appointment")
        self._keep_max_date()
        logging.debug(f"Removed rows where student had a more recent appointment")
        self._add_past_followup_count()
        logging.debug(f"Added previous followup appointment count")

    def get_results(self):
        return self._results

    def _filter_year(self):
        self._appointments.filter_year(self._year)

    def _filter_months(self):
        self._appointments.filter_months(self._months)

    def _filter_schools(self):
        # print(self._valid_schools)
        self._appointments.filter_schools(self._valid_schools)

    def _get_all_need_followup(self):
        app_type_col = self._appointments.get_col(Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')
        self._results = self._appointments.get_df()[
            self._appointments.get_df()[app_type_col].str.startswith(self._appointment_types["include"])
            & ~(self._appointments.get_df()[app_type_col].isin(self._appointment_types["disclude"]))
            ]
        # print(self._appointment_types["include"])
        # print(self._appointment_types["disclude"])

    def _remove_followed_up(self):
        date_col = self._appointments.get_col(Column.DATE)

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
        date_col = self._appointments.get_col(Column.DATE)
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        self._results = self._results.loc[self._results.groupby(email_col)[date_col].idxmax()]

    def _get_latest_valid_followup_dates(self) -> pd.DataFrame:
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        date_col = self._appointments.get_col(Column.DATE)
        valid_followup = self._get_followup_appointments()
        logging.debug(f"got valid followup appointments")
        return valid_followup.groupby(email_col)[date_col].max().reset_index(
            name=self._latest_followup_col
        )

    def _add_latest_followup(self):
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
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
