import logging
from typing import Self
import pandas as pd
from src.dataset.appointment_status import AppointmentStatus

from src.dataset.column import Column
from src.utils.df_utils import sort_columns_by_date
from src.utils.general_utils import get_month_range

from enum import Enum

from src.utils.type_utils import FilterType


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

    def deep_copy(self) -> Self:
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
        try:
            self.get_col(Column.DATE)
        except ValueError:
            raise ValueError("DataFrame must have a date column")
        self.set_df(sort_columns_by_date(self.get_df(), self.get_col_name(Column.DATE)))

    def reset_index(self) -> None:
        self.set_df(self.get_df().reset_index(drop=True))

    def filter_months(self, *months: str) -> None:
        if not months:
            month_input = get_months_input()
            month_input = month_input.strip()
            months = tuple(month_input.split(','))

        # Separate month ranges into individual months
        month_set = DataSet.split_month_ranges(months)
        if not month_set or len(month_set) == 0:
            raise ValueError(f"Invalid month input {months}")

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

    def filter_staff_emails(self, emails: FilterType):
        self.filter_by_col(Column.STAFF_EMAIL, emails)

    def filter_student_emails(self, emails: FilterType):
        self.filter_by_col(Column.STUDENT_EMAIL, emails)

    def filter_appointment_status(self):
        def map_values(enum_obj: Enum) -> str:
            if isinstance(enum_obj, str):
                return enum_obj
            return ''
        valid = list(map(map_values, AppointmentStatus.VALID_SCHEDULED.value))
        valid_scheduled = FilterType(
            include=valid,
            exclude=None
        )
        self.filter_by_col(Column.STATUS, valid_scheduled)

    def filter_by_col(self, col: Enum, filter: FilterType):
        if not filter:
            logging.debug("No filter to apply")
            return
        if not isinstance(filter, FilterType):
            logging.warn("Invalid filter type")
            return
        if not isinstance(col, Column):
            logging.warn("Invalid column type")
            return

        self.get_col(col).fillna("None", inplace=True)
        self.get_df().drop(
            self.get_df()[
                ~self.get_col(col).str.contains(filter.get_include()) | self.get_col(col).str.contains(filter.get_exclude())
            ].index,
            inplace=True
        )

    def filter_majors(self, majors: FilterType):
        self.filter_by_col(Column.STUDENT_MAJOR, majors)

    def filter_schools(self, schools: FilterType):
        self.filter_by_col(Column.STUDENT_COLLEGE, schools)

    def filter_appointment_type(self, appointment_types: FilterType):
        self.filter_by_col(Column.APPOINTMENT_TYPE, appointment_types)


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
