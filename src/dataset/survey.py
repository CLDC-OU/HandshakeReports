from enum import Enum
import re
import pandas as pd
from src.dataset.dataset import DataSet


class SurveyDataSet(DataSet):
    type_name = 'survey_results'

    class Column(Enum):
        DATE = DataSet.Column.DATE.value
        ID = DataSet.Column.ID.value
        STUDENT_EMAIL = 'stu_email'
        STUDENT_FIRST_NAME = 'fname'
        STUDENT_LAST_NAME = 'lname'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)
        self._remove_numbers_from_columns()

    @staticmethod
    def _remove_numbers_from_column(column_name):
        return re.sub(r'^[0-9\W]+', '', column_name)

    def _remove_numbers_from_columns(self) -> None:
        self.get_df().columns = self.get_df().columns.map(
            SurveyDataSet._remove_numbers_from_column
        )
