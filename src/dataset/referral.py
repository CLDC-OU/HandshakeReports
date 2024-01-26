from enum import Enum
import logging
import pandas as pd
from src.dataset.dataset import DataSet
from src.utils.type_utils import FilterType


class ReferralDataSet(DataSet):
    type_name = 'referral'

    class Column(Enum):
        DATE = DataSet.Column.DATE
        ID = DataSet.Column.ID
        STAFF_EMAIL = 'staff_email'
        STUDENT_EMAIL = 'stu_email'
        STUDENT_COLLEGE = 'college'
        STUDENT_MAJOR = 'major'
        STUDENT_CLASS = 'class'
        STUDENT_CARD_ID = 'card_id'
        STUDENT_FIRST_NAME = 'fname'
        STUDENT_PREFERRED_NAME = 'pref_name'
        STUDENT_LAST_NAME = 'lname'
        UNIQUE_REFERRAL = 'unique_referral'
        REFERRING_DEPARTMENT = 'referring_department'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)

    def filter_department(self, department: FilterType):
        rows_before = len(self.get_df())
        self.filter_by_col(ReferralDataSet.Column.REFERRING_DEPARTMENT, department)
        logging.debug(f"Filtered out {rows_before - len(self.get_df())} rows")
