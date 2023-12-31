import pandas as pd


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

def filter_target_isin(df, col, li):
    df = df[df[col].isin(li)]
    return df

def filter_target_pattern_isin(df:pd.DataFrame, col:str, patterns:list):
    df[col] = fill_na(df, col)
    pattern = '|'.join(patterns)
    df = df[df[col].str.contains(pattern, regex=True, case=False)]
    return df

def fill_na(df, col):
    return df[col].fillna('NA')