import pandas as pd
from .DataSet import Column, DataSet
from Utils.df_utils import filter_by_time_diff
from datetime import datetime as dt


class SurveyResults():
    def __init__(self, appointments:DataSet, survey_results:DataSet, day_range:int, year:str, months:list, emails:list, remove_cols:list) -> None:
        if appointments.get_type() != DataSet.Type.APPOINTMENT or survey_results.get_type() != DataSet.Type.SURVEY:
            print(f'[SurveyResults {dt.now()}] Invalid DataSet types provided at filter_appointment_surveys')
            return False
        self._appointments = appointments
        self._survey_results = survey_results
        self._results = None
        self._day_range = day_range
        self._year = year
        self._months = months
        self._emails = emails
        if not remove_cols:
            self.remove_cols = ['Time_Difference']
        else:
            self.remove_cols = remove_cols + ['Time_Difference']
        self.rename_cols = None
        self.final_cols = None
    
    def run_report(self) -> None:
        self._appointments.sort_date()
        print(f"[SurveyResults {dt.now()}] sorted appointments by date")
        self._survey_results.sort_date()
        print(f"[SurveyResults {dt.now()}] sorted survey results by date")

        self._appointments.filter_appointment_status()
        print(f"[SurveyResults {dt.now()}] filtered valid appointment statuses")
        self._appointments.filter_year(self._year)
        print(f"[SurveyResults {dt.now()}] filtered year")
        self._appointments.filter_months(self._months)
        print(f"[SurveyResults {dt.now()}] filtered months")
        self._appointments.filter_staff_emails(self._emails)
        print(f"[SurveyResults {dt.now()}] filtered staff emails")
        
        self._normalize_email_cols()
        self._results = self._filter_by_time_diff()
        print(f"[SurveyResults {dt.now()}] filtered time difference")

    def get_results(self) -> pd.DataFrame | None:
        return self._results
    
    # ensure the student email columns have the same name. Rename the survey set to match
    def _normalize_email_cols(self) -> None:
        if self._survey_results.get_col(Column.STUDENT_EMAIL) != self._appointments.get_col(Column.STUDENT_EMAIL):
            self._survey_results.get_df().rename(
                {self._survey_results.get_col(Column.STUDENT_EMAIL): self._appointments.get_col(Column.STUDENT_EMAIL)}
            )

    def _filter_by_time_diff(self) -> pd.DataFrame:
        return filter_by_time_diff(
            df_1=self._survey_results.get_df(),
            col_1=self._survey_results.get_col(Column.DATE),
            df_2=self._appointments.get_df(),
            col_2=self._appointments.get_col(Column.DATE),
            days=self._day_range,
            merge_col=self._appointments.get_col(Column.STUDENT_EMAIL),
        )
