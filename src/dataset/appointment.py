from enum import Enum
import logging
import pandas as pd
from dataset.appointment_status import AppointmentStatus
from src.dataset.dataset import DataSet
from utils.type_utils import FilterType


class AppointmentDataSet(DataSet):
    type_name = 'appointments'

    class Column(Enum):
        DATE = DataSet.Column.DATE
        ID = DataSet.Column.ID
        STAFF_EMAIL = 'staff_email'
        APPOINTMENT_TYPE = 'type'
        STUDENT_EMAIL = 'stu_email'
        STUDENT_COLLEGE = 'college'
        STUDENT_MAJOR = 'major'
        STUDENT_CLASS = 'class'
        STUDENT_CARD_ID = 'card_id'
        STUDENT_FIRST_NAME = 'fname'
        STUDENT_PREFERRED_NAME = 'pref_name'
        STUDENT_LAST_NAME = 'lname'
        STATUS = 'status'
        DATE_SCHEDULED = 'date_scheduled'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)

    def filter_staff_emails(self, emails: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(AppointmentDataSet.Column.STAFF_EMAIL, emails)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")

    def filter_student_emails(self, emails: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(AppointmentDataSet.Column.STUDENT_EMAIL, emails)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")

    def filter_appointment_status(self):
        rows_before = len(self.get_df())

        def map_values(enum_obj: Enum) -> str:
            if isinstance(enum_obj, str):
                return enum_obj
            return ''
        valid = list(map(map_values, AppointmentStatus.VALID_SCHEDULED.value))
        valid_scheduled = FilterType(
            include=valid,
            exclude=None
        )
        self.filter_by_col(AppointmentDataSet.Column.STATUS, valid_scheduled)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")

    def filter_appointment_type(self, appointment_types: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(AppointmentDataSet.Column.APPOINTMENT_TYPE, appointment_types)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")

    def filter_majors(self, majors: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(AppointmentDataSet.Column.STUDENT_MAJOR, majors)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")

    def filter_schools(self, schools: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(AppointmentDataSet.Column.STUDENT_COLLEGE, schools)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")
