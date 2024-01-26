from enum import Enum
import pandas as pd
from src.dataset.dataset import DataSet


class EnrollmentDataSet(DataSet):
    type_name = 'enrollment'

    class Column(Enum):
        DATE = DataSet.Column.DATE.value
        ID = DataSet.Column.ID.value
        STUDENT_CARD_ID = 'card_id'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)
