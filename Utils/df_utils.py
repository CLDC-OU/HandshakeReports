from argparse import ArgumentTypeError
import pandas as pd
from Utils.file_utils import filter_files, get_most_recent_file


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


def remove_columns(df, cols):
    if not cols:
        return df
    if len(cols) == 0:
        return df
    return df.drop(columns=cols)


def filter_columns(df, columns_to_display):
    if columns_to_display:
        if len(columns_to_display) > 0:
            return df[columns_to_display]
        return df
    return df


def sort_columns_by_date(df, column_name):
    df[column_name] = pd.to_datetime(df[column_name]).dt.tz_localize(None)
    df.sort_values(by=column_name, inplace=True)
    return df


def filter_by_time_diff(df_1, col_1, df_2, col_2, days, merge_col):
    df_1[col_1] = pd.to_datetime(df_1[col_1]).dt.tz_localize(None)
    df_2[col_2] = pd.to_datetime(df_2[col_2]).dt.tz_localize(None)
    merged_df = pd.merge_asof(df_1, df_2,
                              left_on=col_1,
                              right_on=col_2,
                              by=merge_col,
                              direction='backward',
                              tolerance=pd.Timedelta(days=days))
    merged_df['Time_Difference'] = merged_df[col_1] - merged_df[col_2]
    # Filter rows where the survey was completed after the appointment
    return merged_df[merged_df['Time_Difference'] > pd.Timedelta(days=0)]


def filter_target_isin(df: pd.DataFrame, col: str, li: list) -> None:
    df.drop(
        df[~df[col].isin(li)].index,
        inplace=True
    )
    # df = df[df[col].isin(li)]


def filter_target_pattern_isin(df: pd.DataFrame, col: str | None, patterns: list):
    if col is None:
        raise ArgumentTypeError('Column cannot be None')
    df[col] = fill_na(df, col)
    pattern = '|'.join(patterns)
    df.drop(
        df[~df[col].str.contains(pattern, regex=True, case=False)].index,
        inplace=True
    )


def fill_na(df, col):
    return df[col].fillna('NA')
