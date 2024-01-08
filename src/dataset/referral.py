from enum import Enum
import pandas as pd
from dataset.dataset import DataSet


class ReferralDataSet(DataSet):
    type_name = 'referral'

    def __init__(self, id: str, df: pd.DataFrame, cols: dict) -> None:
        super().__init__(id, df, cols)
