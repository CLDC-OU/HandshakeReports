from enum import Enum
import pandas as pd
from dataset.dataset import DataSet


class SurveyDataSet(DataSet):
    type_name = 'survey_results'

    class Column(Enum, DataSet.Column):  # type: ignore
        ID = 'id'
        DATE = 'date'
        STUDENT_EMAIL = 'stu_email'
        STUDENT_FIRST_NAME = 'fname'
        STUDENT_LAST_NAME = 'lname'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)

