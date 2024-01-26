import logging
import pandas as pd
from src.dataset.appointment import AppointmentDataSet
from src.dataset.enrollment import EnrollmentDataSet
from src.dataset.referral import ReferralDataSet

from src.dataset.appointment_status import AppointmentStatus
from src.dataset.dataset import DataSet
from src.reports.report import Report
from src.utils.type_utils import FilterType


class Referrals(Report):
    def __init__(self, referrals: ReferralDataSet, appointment: AppointmentDataSet, valid_departments: FilterType, complete_types: FilterType, enrollment: DataSet | None = None, merge_on: EnrollmentDataSet.Column | None = None) -> None:
        self._referrals = referrals
        self._appointment = appointment
        self.valid_departments = valid_departments
        self._valid_appointment_pattern = complete_types
        self._enrollment = enrollment
        self._merge_on = merge_on
        self._appointment_cols = [appointment.get_col(AppointmentDataSet.Column.STUDENT_EMAIL), appointment.get_col(DataSet.Column.DATE),
                                  appointment.get_col(AppointmentDataSet.Column.STATUS)]
        self.results = pd.DataFrame(None)

    @property
    def valid_departments(self) -> FilterType:
        return self._valid_departments

    @valid_departments.setter
    def valid_departments(self, value: FilterType) -> None:
        if not isinstance(value, FilterType):
            raise TypeError("Departments is not a DepartmentsFilter")
        self._valid_departments = value

    def run_report(self) -> None:
        self._filter_valid_appointments()
        logging.debug("Filtered valid appointment types in appointments DataSet")

        self.filter_valid_departments()
        logging.debug("Filtered valid referring departments in referrals DataSet")

        self._normalize_email_col()
        logging.debug("Normalized email columns between appointments and referrals DataSet")

        self._merge_referrals()
        logging.debug("Merged referrals DataSet with appointments DataSet")

        self._remove_past_appointments()
        logging.debug("Removed appointments from before the referral date")

        self._re_merge()
        logging.debug("Re-merged removed referrals into results")

        self._add_scheduled()
        logging.debug("Added appointment scheduled columns")
        self._add_completed()
        logging.debug("Added appointment completed columns")

        self._set_preferred_name()
        logging.debug("Set student name to preferred name")
        self._merge_enrollment()
        logging.debug("Merged enrollment data")
        self._remove_duplicates()
        logging.debug("Removed duplicate rows")

    @property
    def results(self) -> pd.DataFrame:
        if not isinstance(self._results, pd.DataFrame):
            raise TypeError("Results is not a DataFrame")
        return self._results

    @results.setter
    def results(self, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Results is not a DataFrame")
        self._results = value

    def get_results(self) -> pd.DataFrame:
        return self.results

    def _remove_duplicates(self):
        unique_col = self._referrals.get_col_name(ReferralDataSet.Column.UNIQUE_REFERRAL)
        if unique_col is None:
            logging.debug(
                "No unique col name to remove duplicates. This is expected behavior if no unique_col is specified in files.config.json")
            return
        self.results.drop_duplicates(inplace=True, subset=[unique_col])
        logging.debug(f"Removing duplicate referral rows on: {unique_col}")
        rows_before = len(self._referrals.get_df())
        logging.debug(f"Removed {rows_before - len(self._referrals.get_df())} duplicate referral rows")

    def _add_scheduled(self):
        dates = self.results[self._appointment.get_col_name(AppointmentDataSet.Column.DATE_SCHEDULED)].values.tolist()
        scheduled = list(map(lambda x: "FALSE" if pd.isna(x) else "TRUE", dates))

        self.results.insert(
            loc=0,
            column="Scheduled",
            value=scheduled
        )

    def _merge_enrollment(self):
        self._normalize_card_id()
        # make sure card ids are normalized and then merge enrollment data with it, then check that all of the correct data is there and there aren't any key errors
        if self._enrollment:
            self.results = pd.merge(
                left=self.results,
                right=self._enrollment.get_df(),
                on=self._merge_on,
                how="left",
                suffixes=('', '_')
            )

    def _set_preferred_name(self):
        pref_names = self.results[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_PREFERRED_NAME)].values.tolist()
        f_names = self.results[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_FIRST_NAME)].values.tolist()
        names = []
        for i in range(len(f_names)):
            names.append((pref_names[i], f_names[i]))

        names = list(map(lambda x: x[1] if pd.isna(x[0]) else x[0], names))
        self.results[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_FIRST_NAME)] = names

    def _add_completed(self):
        statuses = self.results[self._appointment.get_col_name(AppointmentDataSet.Column.STATUS)].values.tolist()
        completed = list(map(lambda x: "TRUE" if x in AppointmentStatus.VALID_COMPLETED.value else "FALSE", statuses))

        self.results.insert(
            loc=0,
            column="Completed",
            value=completed
        )

    def _filter_valid_appointments(self) -> None:
        self._appointment.filter_appointment_type(self._valid_appointment_pattern)

    def filter_valid_departments(self) -> None:
        self._referrals.filter_department(self.valid_departments)

    def _merge_referrals(self):
        self.results = pd.merge(
            left=self._referrals.get_df(),
            right=self._appointment.get_df(),
            how="outer",
            on=self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL)
        )

    def _normalize_email_col(self) -> str:
        appointment_col = self._appointment.get_col_name(AppointmentDataSet.Column.STUDENT_EMAIL)
        referral_col = self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL)
        if not appointment_col or not referral_col:
            raise ValueError("Appointment or referral email column is not defined")
        if appointment_col != referral_col:
            self._appointment.set_df(self._appointment.df.rename(
                columns={appointment_col: referral_col}
            ))

        return referral_col

    def _normalize_card_id(self):
        if not self._enrollment:
            return
        enrollment_col = self._enrollment.get_col_name(EnrollmentDataSet.Column.STUDENT_CARD_ID)
        referral_col = self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_CARD_ID)
        if referral_col != enrollment_col:
            self.results = self.results.rename(
                columns={referral_col: enrollment_col}
            )
        self.results[enrollment_col] = self.results[enrollment_col].str.replace(r'^G', '', regex=True).fillna(
            -1).astype(int)

    def _remove_past_appointments(self):
        # first remove any null referral dates (students that had a valid appointment but not a referral)
        self.results = self.results[~self.results[self._referrals.get_col_name(Column.DATE)].isnull()]
        # keep students in results who had a referral after their most recent valid appointment, or have not had any valid appointment
        self.results = self.results[~self.results[self._referrals.get_col_name(Column.DATE)].isna()]
        self._format_referral_dates()
        # self.results = self.results[~(
        #     (self.results[self._appointment.get_col_name(Column.DATE)].dt.day_of_year < self.results[
        #         self._referrals.get_col_name(Column.DATE)].dt.day_of_year) | (
        #             self.results[self._appointment.get_col_name(Column.DATE)].dt.year < self.results[
        #                 self._appointment.get_col_name(Column.DATE)].dt.year)
        # )]
        self.results = self.results[~(
            (self.results[self._appointment.get_col_name(Column.DATE)] < self.results[
                self._referrals.get_col_name(Column.DATE)])
        )]

    def _format_referral_dates(self):
        self.results[self._referrals.get_col_name(ReferralDataSet.Column.DATE)] = pd.to_datetime(
            self.results[self._referrals.get_col_name(ReferralDataSet.Column.DATE)]).dt.tz_localize(None)
        # self._results[self._referrals.get_col(Column.DATE)] = self._results[self._referrals.get_col(Column.DATE)].str.replace(' GMT-0400 (Eastern Daylight Time)', '')
        # self._results[self._referrals.get_col(Column.DATE)] = pd.to_datetime(self._results[self._referrals.get_col(Column.DATE)], format='%a %b %d %Y %H:%M:%S').dt.strftime('%Y-%m-%d')

    def _re_merge(self):
        self.results = pd.merge(
            left=self._referrals.get_df(),
            right=self.results,
            how="outer",
            on=self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL),
            suffixes=('', '_')
        )

    def _repair_only_past_appointments(self):
        # from referrals add rows for students that are no longer in results

        # get a list of unique emails in referrals
        ref_emails = self._referrals.get_df()[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL)].unique()
        # get a list of unique emails in results
        res_emails = self.results[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL)].unique()
        emails = list(set(ref_emails) - set(res_emails))
        self._referrals.get_df()[self._referrals.get_col_name(ReferralDataSet.Column.STUDENT_EMAIL)][emails]
