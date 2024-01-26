import logging
import pandas as pd
from dataset.appointment import AppointmentDataSet
from dataset.enrollment import EnrollmentDataSet
from dataset.referral import ReferralDataSet

from src.dataset.appointment_status import AppointmentStatus
from src.dataset.dataset import DataSet
from src.reports.report import Report
from src.utils.type_utils import DepartmentFilter, DepartmentsFilter, FilterType


class Referrals(Report):
    def __init__(self, referrals: ReferralDataSet, appointment: AppointmentDataSet, departments: DepartmentsFilter, complete_types: FilterType, enrollment: DataSet | None = None, merge_on: EnrollmentDataSet.Column | None = None) -> None:
        self._referrals = referrals
        self._appointment = appointment
        self.departments = departments
        self._valid_appointment_pattern = complete_types
        self._enrollment = enrollment
        self._merge_on = merge_on
        self._appointment_cols = [appointment.get_col(AppointmentDataSet.Column.STUDENT_EMAIL), appointment.get_col(DataSet.Column.DATE),
                                  appointment.get_col(AppointmentDataSet.Column.STATUS)]
        self.results = pd.DataFrame(None)

    @property
    def departments(self) -> DepartmentsFilter:
        return self._departments

    @departments.setter
    def departments(self, value: DepartmentsFilter) -> None:
        if not isinstance(value, DepartmentsFilter):
            raise TypeError("Departments is not a DepartmentsFilter")
        self._departments = value

    def run_report(self) -> None:
        full_results = pd.DataFrame(None)
        self._appointment_copy = self._appointment.deep_copy()
        self._referral_copy = self._referrals.deep_copy()
        for department in self.departments:
            self._filter_valid_appointments()
            logging.debug("Filtered base valid appointment types")
            self._filter_valid_appointments(department)
            logging.debug(f"Filtered valid appointment types for {department} referrals")
            self._normalize_email_col()
            logging.debug("Normalized email column")
            self._merge_referrals()
            logging.debug("Merged referrals with appointments")
            self._remove_past_appointments()
            logging.debug("Removed past appointments")
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
            full_results.add(self.results, fill_value=0)
            logging.debug("Added results to full results")
            if self.departments.__next__() is not None:
                self._appointment = self._appointment_copy.deep_copy()
                self._referrals = self._referral_copy.deep_copy()

        self.results = full_results
        self._re_merge()
        logging.debug("Re-merged removed referrals")

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
                "No unique col name to remove duplicates. If no unique_col is specified in files.config.json, this is expected behavior.")
            return
        logging.debug(f"Removing duplicate rows on: {unique_col}")
        self.results.drop_duplicates(inplace=True, subset=[unique_col])
        logging.debug("Removed duplicate rows")

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

    def _filter_valid_appointments(self, department: DepartmentFilter | None = None) -> None:
        if department is None:
            self._appointment.filter_appointment_type(self._valid_appointment_pattern)
            return
        if not isinstance(department, DepartmentFilter):
            raise TypeError("Department is not a DepartmentFilter")

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
