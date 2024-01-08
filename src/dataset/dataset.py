import re
import pandas as pd
from enum import Enum

from utils.file_utils import filter_files, get_most_recent_file
from .appointment_status import AppointmentStatus
from dataset.column import Column
from utils.df_utils import filter_target_isin, filter_target_pattern_isin, sort_columns_by_date
from utils.general_utils import get_month_range



class DataSet:
    type_name = None

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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, DataSet):
            return self.get_id() == __value.get_id()
        return False

    def deep_copy(self) -> DataSet:
        return self.__class__(self.id, self.df.copy(deep=True), self.cols.copy())

    def same_type(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return True
        return False

    def get_id(self) -> str:
        return self.id

    def get_df(self) -> pd.DataFrame:
        return self.df

    def get_col(self, col_id: Enum) -> pd.Series:
        if not isinstance(col_id, Column):
            raise ValueError("col_id must be a Column Enum")
        if col_id.value not in self.cols:
            raise ValueError("col_id must be a defined column")
        if self.get_col_name(col_id) not in self.get_df().columns:
            raise ValueError("col_id must be in DataFrame")

        return self.get_df()[self.get_col_name(col_id)]

    def get_col_name(self, col_id: Enum) -> str | None:
        if not isinstance(col_id, Column):
            raise ValueError("col_id must be a Column Enum")

        if col_id.value in self.cols:
            return self.cols[col_id.value]
        return None

    def set_df(self, df) -> None:
        self.df = df

    def sort_date(self) -> None:
        self.set_df(sort_columns_by_date(self.get_df(), self.get_col(Column.DATE)))


    def filter_months(self, *months: str) -> None:
        if not months:
            month_input = get_months_input()
            month_input = month_input.strip()
            months = tuple(month_input.split(','))

        # Separate month ranges into individual months
        month_set = DataSet.split_month_ranges(months)
        if not month_set or len(month_set) == 0:
            raise ValueError("Invalid month input")

        # Filter DataFrame by month
        self.get_df().drop(
            self.get_df()[~self.get_col(Column.DATE).dt.strftime('%B').isin(month_set)].index,
            inplace=True
        )

    @staticmethod
    def split_month_range(range: str) -> list[str]:
        if '-' in range:
            split_range = range.split('-')
            split_range[0] = split_range[0].strip()
            split_range[1] = split_range[1].strip()
            range_list = get_month_range(split_range[0], split_range[1])
        else:
            range_list = get_month_range(range)
        return range_list

    @staticmethod
    def split_month_ranges(ranges: tuple[str, ...]) -> set[str]:
        month_set = set()
        for range in ranges:
            month_set.update(DataSet.split_month_range(range))
        return month_set

    @staticmethod
    def split_year_range(year_range: str) -> list[str]:
        if '-' in year_range:
            split_range = year_range.split('-')
            split_range[0] = split_range[0].strip()
            split_range[1] = split_range[1].strip()
            if not split_range[0].isdigit() or not split_range[1].isdigit():
                raise ValueError("Invalid year range - start year and end year must be parseable as integers")
            if int(split_range[0]) > int(split_range[1]):
                raise ValueError("Invalid year range - start year must be less than end year")
            range_list = list(range(
                int(split_range[0]), int(split_range[1]) + 1
            ))
            str_list = []
            for i in range(len(range_list)):
                str_list.append(str(range_list[i]))
        else:
            if not year_range.isdigit():
                raise ValueError("Invalid year range - year must be parseable as integer")
            str_list = [year_range]
        return str_list

    @staticmethod
    def split_year_ranges(year_ranges: tuple[str, ...]) -> set[str]:
        year_set = set()
        for year_range in year_ranges:
            year_set.update(DataSet.split_year_range(year_range))
        return year_set

    def filter_years(self, *years: str):
        if not years:
            year_input = get_year_input()
            year_input.strip()
            years = tuple(year_input.split(','))

        # Separate year ranges into individual years
        year_set = DataSet.split_year_ranges(years)

        # Filter DataFrame by years
        self.get_df().drop(
            self.get_df()[~self.get_col(Column.DATE).dt.strftime('%Y').isin(year_set)].index,
            inplace=True
        )

    def filter_staff_emails(self, emails: list):
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
