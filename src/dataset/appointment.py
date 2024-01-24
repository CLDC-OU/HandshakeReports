from enum import Enum
import pandas as pd
from src.dataset.dataset import DataSet


class AppointmentDataSet(DataSet):
    type_name = 'appointments'

    class Column(Enum):
        DataSet.Column
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
