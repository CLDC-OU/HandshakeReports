import logging
import math
import pandas as pd
from datetime import datetime as dt

from .AppointmentStatus import AppointmentStatus
from .DataSet import Column, DataSet


class Referrals():
    def __init__(self, referrals:DataSet, appointment:DataSet, valid_appointment_pattern:str, rename_cols:list, final_cols:list, enrollment:DataSet|None = None, merge_on:Column = None) -> None:
        self._referrals = referrals
        # print(set(self._referrals.df))
        self._appointment = appointment
        self._valid_appointment_pattern = valid_appointment_pattern
        self._enrollment = enrollment
        self._merge_on = merge_on
        self._appointment_cols = [appointment.get_col(Column.STUDENT_EMAIL), appointment.get_col(Column.DATE), appointment.get_col(Column.STATUS)]
        self._results = pd.DataFrame(None)
        self.remove_cols = None
        self.rename_cols = rename_cols
        self.final_cols = final_cols

    def run_report(self) -> None:
        self._filter_valid_appointments()
        logging.debug(f"Filtered valid appointments")
        self._normalize_email_col()
        logging.debug(f"Normalized email column")
        self._merge_referrals()
        logging.debug(f"Merged referrals with appointments")
        self._remove_past_appointments()
        logging.debug(f"Removed past appointments")
        self._re_merge()
        logging.debug(f"Re-merged removed referrals")
        self._add_scheduled()
        logging.debug(f"Added appointment scheduled columns")
        self._add_completed()
        logging.debug(f"Added appointment completed columns")
        self._set_preferred_name()
        logging.debug(f"Set student name to preferred name")
        self._merge_enrollment()
        logging.debug(f"Merged enrollment data")
        self._remove_duplicates()

    def get_results(self) -> pd.DataFrame:
        return self._results

    # def run_report(self):
    #     self._filter_valid_appointments()
    #     merge = self._merge_referrals()
    #     unscheduled = self.get_unscheduled()
    #     self._remove_past_appointments()

    def _remove_duplicates(self):
        unique_col = self._referrals.get_col(Column.UNIQUE_REFERRAL)
        if unique_col is None:
            logging.debug("No unique col name to remove duplicates. If no unique_col is specified in files.config.json, this is expected behavior.")
            return
        logging.debug(f"Removing duplicate rows on: {unique_col}")
        self._results.drop_duplicates(inplace=True, subset=[unique_col])
        logging.debug(f"Removed duplicate rows")

    def _add_scheduled(self):
        dates = self._results[self._appointment.get_col(Column.DATE_SCHEDULED)].values.tolist()
        scheduled = list(map(lambda x: "FALSE" if pd.isna(x) else "TRUE", dates))
        
        self._results.insert(
            loc=0,
            column="Scheduled",
            value=scheduled
        )
    
    def _merge_enrollment(self):
        self._normalize_card_id()
        # make sure card ids are normalized and then merge enrollment data with it, then check that all of the correct data is there and there aren't any key errors
        if self._enrollment:
            self._results = pd.merge(
                left=self._results,
                right=self._enrollment.get_df(),
                on=self._merge_on,
                how="left",
                suffixes=('', '_')
            )
        

    def _set_preferred_name(self):
        pref_names = self._results[self._referrals.get_col(Column.STUDENT_PREFERRED_NAME)].values.tolist()
        f_names = self._results[self._referrals.get_col(Column.STUDENT_FIRST_NAME)].values.tolist()
        names = []
        for i in range(len(f_names)):
            names.append((pref_names[i], f_names[i]))

        names = list(map(lambda x: x[1] if pd.isna(x[0]) else x[0], names))
        self._results[self._referrals.get_col(Column.STUDENT_FIRST_NAME)] = names
        # self.__results[self.referrals.get_col(Column.STUDENT_FIRST_NAME)] = self.__results[
        #     self.referrals.get_col(Column.STUDENT_PREFERRED_NAME) 
        #         if self.__results[self.referrals.get_col(Column.STUDENT_PREFERRED_NAME)].notnull() 
        #         else self.__results[self.referrals.get_col(Column.STUDENT_FIRST_NAME)]]

    def _add_completed(self):
        statuses = self._results[self._appointment.get_col(Column.STATUS)].values.tolist()
        completed = list(map(lambda x: "TRUE" if x in AppointmentStatus.VALID_COMPLETED.value else "FALSE", statuses))
        
        self._results.insert(
            loc=0,
            column="Completed",
            value=completed
        )

    def _filter_valid_appointments(self):
        self._appointment.filter_appointment_type(self._valid_appointment_pattern)
    
    # def get_unscheduled(self):
    #     # get list of unique student emails that have an appointment
    #     li = self.appointment.get_df()[self.appointment.get_col(Column.STUDENT_EMAIL)].drop_duplicates().to_list()
    #     return filter_target_isin(self.referrals.get_df(), self.referrals.get_col(Column.STUDENT_EMAIL) , li)
    
    def _merge_referrals(self):
        self._results = pd.merge(
            left=self._referrals.get_df(),
            right=self._appointment.get_df(),
            how="outer",
            on=self._referrals.get_col(Column.STUDENT_EMAIL)
        )

    # def _merge_referrals(self):
    #     col = self._normalize_email_col()
    #     self.appointment.set_df(pd.merge(
    #         left=self.appointment.get_df()[self.appointment_cols],
    #         right=self.referrals.get_df(),
    #         on=col,
    #         how="left"
    #     ))
    
    def _normalize_email_col(self) -> str:
        appointment_col = self._appointment.get_col(Column.STUDENT_EMAIL)
        referral_col = self._referrals.get_col(Column.STUDENT_EMAIL)
        if appointment_col != referral_col:
            self._appointment.set_df(self._appointment.df.rename(
                columns={appointment_col: referral_col}
            ))

        return referral_col
    
    def _normalize_card_id(self):
        enrollment_col = self._enrollment.get_col(Column.STUDENT_CARD_ID)
        referral_col = self._referrals.get_col(Column.STUDENT_CARD_ID)
        if referral_col != enrollment_col:
            self._results = self._results.rename(
                columns={referral_col: enrollment_col}
            )
        self._results[enrollment_col] = self._results[enrollment_col].str.replace(r'^G', '', regex=True).fillna(-1).astype(int)
    
    def _remove_past_appointments(self):
        # first remove any null referral dates (students that had a valid appointment but not a referral)
        self._results = self._results[~self._results[self._referrals.get_col(Column.DATE)].isnull()]
        # keep students in results who had a referral after their most recent valid appointment, or have not had any valid appointment 
        self._results = self._results[~self._results[self._referrals.get_col(Column.DATE)].isna()]
        self._format_referral_dates()
        self._results = self._results[~(
            (self._results[self._appointment.get_col(Column.DATE)].dt.day_of_year < self._results[self._referrals.get_col(Column.DATE)].dt.day_of_year)
            | (self._results[self._appointment.get_col(Column.DATE)].dt.year < self._results[self._appointment.get_col(Column.DATE)].dt.year)
            )]

    def _format_referral_dates(self):
        self._results[self._referrals.get_col(Column.DATE)] = pd.to_datetime(self._results[self._referrals.get_col(Column.DATE)]).dt.tz_localize(None)
        # self._results[self._referrals.get_col(Column.DATE)] = self._results[self._referrals.get_col(Column.DATE)].str.replace(' GMT-0400 (Eastern Daylight Time)', '')
        # self._results[self._referrals.get_col(Column.DATE)] = pd.to_datetime(self._results[self._referrals.get_col(Column.DATE)], format='%a %b %d %Y %H:%M:%S').dt.strftime('%Y-%m-%d')

    def _re_merge(self):
        self._results = pd.merge(
            left=self._referrals.get_df(),
            right=self._results,
            how="outer",
            on=self._referrals.get_col(Column.STUDENT_EMAIL),
            suffixes=('', '_')
        )

    def _repair_only_past_appointments(self):
        # from referrals add rows for students that are no longer in results
        
        # get a list of unique emails in referrals
        ref_emails = self._referrals.get_df()[self._referrals.get_col(Column.STUDENT_EMAIL)].unique()
        # get a list of unique emails in results
        res_emails = self._results[self._referrals.get_col(Column.STUDENT_EMAIL)].unique()
        emails = list(ref_emails) - list(res_emails)
        self._referrals.get_df()[self._referrals.get_col(Column.STUDENT_EMAIL)][emails]

    # def _remove_past_appointments(self):
    #     df = self.appointment.get_df()
    #     self.appointment.set_df(
    #         df[df[self.appointment.get_col(Column.DATE)] > df[self.referrals.get_col(Column.DATE)]]
    #     )


    # def combine(self):
    #     pd.concat([self.appointment.get_df(), self.referrals.get_df().reindex(self.appointment.get_df().index)], axis=1)