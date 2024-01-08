import re
import pandas as pd
from enum import Enum

from utils.file_utils import filter_files, get_most_recent_file
from .appointment_status import AppointmentStatus
from dataset.column import Column
from utils.df_utils import filter_target_isin, filter_target_pattern_isin, sort_columns_by_date
from utils.general_utils import get_month_range



class DataSet:
    def deep_copy(self):
        return DataSet(self.type.value, self.id, self.df, self.cols)

    def __init__(self, type: str, id: str, df: pd.DataFrame, cols: dict):
        if type == DataSet.Type.APPOINTMENT.value:
            self.type = DataSet.Type.APPOINTMENT
        elif type == DataSet.Type.SURVEY.value:
            self.type = DataSet.Type.SURVEY
        elif type == DataSet.Type.REFERRAL.value:
            self.type = DataSet.Type.REFERRAL
        elif type == DataSet.Type.ENROLLMENT.value:
            self.type = DataSet.Type.ENROLLMENT
        else:
            return
    class Column(Enum):
        ID = 'id'
        DATE = 'date'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("df must be a valid DataFrame")
        if not cols or not isinstance(cols, dict):
            raise ValueError("cols must be a valid dictionary")
        self.id = id
        self.df = df
        self.cols = cols

    def __str__(self) -> str:
        return self.id

    def equal(self, value: object):
        return self.get_id() == value.get_id()

    def same_type(self, value: object):
        return self.get_type() == value.get_type()

    def get_type(self) -> Type:
        return self.type

    def get_id(self) -> str:
        return self.id

    def get_df(self) -> pd.DataFrame:
        return self.df

    def get_col(self, col_id: Column) -> str | None:
        if col_id.value in self.cols:
            return self.cols[col_id.value]
        return None

    def set_df(self, df) -> None:
        self.df = df

    def sort_date(self) -> None:
        self.set_df(sort_columns_by_date(self.get_df(), self.get_col(Column.DATE)))

    def filter_months(self, months):
        if not months:
            months = get_months_input()
        # separate month ranges by commas
        month_ranges = [m.strip() for m in months.split(',')]

        months = []
        # separate ranges by dashes
        for r in month_ranges:
            r = r.split('-')
            months.extend(get_month_range(r))

        # Filter dataframe by month
        self.set_df(self.get_df()[self.get_df()[self.get_col(Column.DATE)].dt.strftime('%B').isin(months)])
        return self.get_df()

    def filter_year(self, year):
        if not year:
            year = get_year_input()
        # Filter dataframe by year
        self.set_df(self.get_df()[self.get_df()[self.get_col(Column.DATE)].dt.strftime('%Y') == year])
        return self.get_df()

    def filter_staff_emails(self, emails):
        if not emails:
            emails = get_emails_input()
        self.set_df(filter_target_isin(self.get_df(), self.get_col(Column.STAFF_EMAIL), emails))

    def filter_student_emails(self, emails):
        if not emails:
            emails = get_emails_input()
        self.set_df(filter_target_isin(self.get_df(), self.get_col(Column.STUDENT_EMAIL), emails))

    def filter_appointment_status(self):
        self.set_df(
            self.get_df()[self.get_df()[self.get_col(Column.STATUS)].isin(AppointmentStatus.VALID_SCHEDULED.value)])
        return self.get_df()

    def filter_majors(self, majors):
        self.set_df(filter_target_pattern_isin(self.get_df(), self.get_col(Column.STUDENT_MAJOR), majors))

    def filter_schools(self, schools):
        self.set_df(filter_target_pattern_isin(self.get_df(), self.get_col(Column.STUDENT_COLLEGE), schools))

    def filter_appointment_type(self, pattern):
        self.set_df(filter_target_pattern_isin(self.get_df(), self.get_col(Column.APPOINTMENT_TYPE), pattern))



def load_df(file_dir: str, must_contain: str, rename_columns: dict, date_col: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(file_dir + "\\" + get_most_recent_file(filter_files(
        file_dir=file_dir,
        must_contain=must_contain,
        file_type=".csv"
    )))
    if rename_columns:
        df.rename(columns=rename_columns, inplace=True)
    if date_col:
        df[date_col] = pd.to_datetime(date_col).dt.tz_localize(None)
    return df


def get_year_input():
    # Prompt for year
    target_year = input("Enter the year you want to filter the data for (e.q. 2023)\n").strip()
    return target_year


def get_months_input():
    # Prompt for month range(s)
    target_months = input(
        "Enter one or more months or month ranges you want to filter the data for (e.g. January-April, "
        "September-December)\n"
    )
    return target_months


def get_emails_input():
    email_input = input("Enter one or more email addresses (comma-separated): ")
    return [email.strip() for email in email_input.split(',')]
