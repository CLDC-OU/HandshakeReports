import pandas as pd
from src.dataset.dataset import DataSet


class EnrollmentDataSet(DataSet):
    type_name = 'enrollment'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)
