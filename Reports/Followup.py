
import pandas as pd
from datetime import datetime as dt
from .DataSet import Column, DataSet


class Followup():
    def __init__(self, appointments:DataSet, enrollment:DataSet, valid_schools:list, year:str, months:list, appointment_types:list, followup_types:list, remove_cols=None, rename_cols=None, final_cols=None) -> None:
        self._appointments = appointments
        self._enrollment = enrollment
        self._results = None
        self._valid_schools = valid_schools
        self._year = year
        self._months = months
        if appointment_types:
            self._appointment_types = appointment_types
            self._latest_followup_col = f'date of last non {self._appointment_types["include"]} appointment'
        else:
            ValueError
            self._appointment_types = None
            self._latest_followup_col = None
        if followup_types:
            self.followup_types = followup_types
        else:
            self.followup_types = None
        self.remove_cols = remove_cols
        self.rename_cols = rename_cols
        self.final_cols = final_cols
    
    def run_report(self):
        self._filter_year()
        print(f"[Followup {dt.now()}] filtered appointment year")
        self._filter_months()
        print(f"[Followup {dt.now()}] filtered appointment months")
        self._filter_schools()
        print(f"[Followup {dt.now()}] filtered student schools")
        self._get_all_need_followup()
        # print(self._appointments.df)
        print(f"[Followup {dt.now()}] filtered students that need a followup {self._latest_followup_col} appointment")
        self._add_latest_followup()
        print(f"[Followup {dt.now()}] added latest followup column")
        self._remove_followed_up()
        print(f"[Followup {dt.now()}] removed rows that already had a followup appointment")
        self._keep_max_date()
        print(f"[Followup {dt.now()}] removed rows where student had a more recent appointment")
        self._add_past_followup_count()
        print(f"[Followup {dt.now()}] added previous followup appointment count")
    
    def get_results(self):
        return self._results

    def _filter_year(self):
        self._appointments.filter_year(self._year)
    def _filter_months(self):
        self._appointments.filter_months(self._months)
    def _filter_schools(self):
        # print(self._valid_schools)
        self._appointments.filter_schools(self._valid_schools)

    def _get_all_need_followup(self):
        app_type_col = self._appointments.get_col(Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')
        self._results = self._appointments.get_df()[
            self._appointments.get_df()[app_type_col].str.startswith(self._appointment_types["include"])
            & ~(self._appointments.get_df()[app_type_col].isin(self._appointment_types["disclude"]))
        ]
        # print(self._appointment_types["include"])
        # print(self._appointment_types["disclude"])

    def _remove_followed_up(self):
        date_col = self._appointments.get_col(Column.DATE)
        
        # keep only rows where the latest followup appointment is before the latest needs followup, or the student has never had a valid followup appointment
        self._results = self._results[(
            (self._results[date_col].notna())
            & (
                (self._results[self._latest_followup_col].isna())
                | (self._results[date_col] >= self._results[self._latest_followup_col])
            )
        )]

    def _keep_max_date(self):
        date_col = self._appointments.get_col(Column.DATE)
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        self._results = self._results.loc[self._results.groupby(email_col)[date_col].idxmax()]

    def _get_latest_valid_followup_dates(self) -> pd.DataFrame:
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        date_col = self._appointments.get_col(Column.DATE)
        valid_followup = self._get_followup_appointments()
        print(f"[Followup {dt.now()}] got valid followup appointments")
        return valid_followup.groupby(email_col)[date_col].max().reset_index(
            name=self._latest_followup_col
        )
    
    def _add_latest_followup(self):
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        self._results = pd.merge(
            left=self._results,
            right=self._get_latest_valid_followup_dates(),
            on=email_col,
            how='left'
        )

    def _add_past_followup_count(self):
        email_col = self._appointments.get_col(Column.STUDENT_EMAIL)
        
        duplicate_appointment_count = self._get_followup_appointments().pivot_table(
            index=[email_col],
            aggfunc='size'
        ).reset_index(name=f'# of past non {self._appointment_types["include"]} appointments')

        self._results = pd.merge(
            left=self._results,
            right=duplicate_appointment_count,
            how="left",
            on=email_col
        )
    
    def _get_followup_appointments(self) -> pd.DataFrame:
        app_type_col = self._appointments.get_col(Column.APPOINTMENT_TYPE)
        self._appointments.get_df()[app_type_col] = self._appointments.get_df()[app_type_col].fillna('MissingData')
        return self._appointments.get_df()[
            ~(self._appointments.get_df()[app_type_col].str.startswith(self._appointment_types["include"]))
            | (self._appointments.get_df()[app_type_col].isin(self._appointment_types["disclude"]))
        ]



    # def run_report(self) -> None:
    #     self.appointments.filter_year(self.year)
    #     self.appointments.filter_months(self.months)
    #     self.appointments.filter_majors(self.valid_majors)

    #     need_followup_appointments = self.get_need_followup_appointments()
    #     followup_appointments = self.get_followup_appointments()

    #     self.merge_latest_need_followup_appointments(need_followup_appointments, followup_appointments)
    #     self.remove_old_followup_appointments(followup_appointments)

    #     self.merge_latest_other_appointments(need_followup_appointments, followup_appointments)
    #     self.merge_duplicate_appointment_count(need_followup_appointments, followup_appointments)

    #     self.get_only_need_followup(self, need_followup_appointments, followup_appointments)

    #     self.results = need_followup_appointments

    # def get_results(self) -> pd.DataFrame | None:
    #     return self.results
    
    # def get_need_followup_appointments(self) -> pd.DataFrame:
    #     self.appointments.get_df()[Column.APPOINTMENT_TYPE] = self.appointments.get_df[Column.APPOINTMENT_TYPE].fillna('MissingData')
    #     return self.appointments.get_df()[
    #         self.appointments.get_df()[Column.APPOINTMENT_TYPE].str.startswith(self.appointment_types["include"])
    #         & ~(self.appointments.get_df()[Column.APPOINTMENT_TYPE].isin(self.appointment_types["disclude"]))
    #     ]
    
    # def get_followup_appointments(self) -> pd.DataFrame:
    #     self.appointments.get_df()[Column.APPOINTMENT_TYPE] = self.appointments.get_df[Column.APPOINTMENT_TYPE].fillna('MissingData')
    #     return self.appointments.get_df()[
    #         ~self.appointments.get_df()[Column.APPOINTMENT_TYPE].str.startswith(self.appointment_types["include"])
    #         or (self.appointments.get_df()[Column.APPOINTMENT_TYPE].isin(self.appointment_types["disclude"]))
    #     ]

    # def merge_latest_need_followup_appointments(self, need_followup, followup):
    #     latest_valid_dates = self.get_latest_valid_dates(need_followup)
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
    #     followup = pd.merge(
    #         left=followup,
    #         right=latest_valid_dates,
    #         on=email_col,
    #         how='left',
    #         suffixes=('', '_latest_valid')
    #     )

    # def remove_old_followup_appointments(self, followup):
    #     date_col = self.appointments.get_col(Column.DATE)
    #     followup = followup[(
    #         followup[date_col] >= followup[date_col + "_latest_valid"]
    #     )]
    
    # def merge_latest_other_appointments(self, need_followup, followup):
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
    #     date_col = self.appointments.get_col(Column.DATE)
    #     latest_other_date = followup.groupby(email_col)[date_col].max().reset_index(
    #         name=f'date of last non ${self.appointment_types["include"]} appointment'
    #     )

    #     need_followup = pd.merge(
    #         left=need_followup,
    #         right=latest_other_date,
    #         how='outer'
    #     )
    
    # def merge_duplicate_appointment_count(self, need_followup, followup):
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
    #     duplicate_appointment_count = followup.pivot_table(
    #         index=[email_col],
    #         aggfunc='size'
    #     ).reset_index(name="# of past appointments")

    #     need_followup = pd.merge(
    #         left=need_followup,
    #         right=duplicate_appointment_count,
    #         how="outer"
    #     )
        
    # def merge_enrollment_data(self, need_followup):
    #     # Merge enrollment data
    #     enrollment_fname = self.enrollment.get_col(Column.STUDENT_FIRST_NAME)
    #     enrollment_lname = self.enrollment.get_col(Column.STUDENT_LAST_NAME)
    #     enrollment_card_id = self.enrollment.get_col(Column.STUDENT_CARD_ID)
    #     appointments_card_id = self.appointments.get_col(Column.STUDENT_FIRST_NAME)
    #     appointments_fname = self.appointments.get_col(Column.STUDENT_LAST_NAME)
    #     appointments_lname = self.appointments.get_col(Column.STUDENT_CARD_ID)

    #     # rename card id column to match the enrollment dataframe (what we will merge on)
    #     need_followup = need_followup.rename(columns={appointments_card_id: enrollment_card_id})
    #     # merge enrollment and valid df on card id column
    #     need_followup = pd.merge(need_followup, self.enrollment.get_df()[[enrollment_card_id, enrollment_fname, enrollment_lname]], on=enrollment_card_id)
    #     # rename columns from enrollment column names to appointment column names
    #     need_followup = need_followup.rename({enrollment_fname: appointments_fname, enrollment_lname: appointments_lname, enrollment_card_id: appointments_card_id})

    # # def remove_followed_up(self, need_followup):
    # #     # remove appointments where there was a followup appointment at a later date
    # #     date_col = self.appointments.get_col(Column.DATE)
    # #     need_followup = need_followup[~(need_followup[date_col].isnull())]

    # def get_only_need_followup(self, need_followup, followup):
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
    #     # Create a list of students that had an appointment that needs a followup (need_followup) and have not had an followup appointment at a later date (followup)
    #     only_need_followup = set(need_followup[email_col]) - set(followup[email_col])
    #     need_followup = need_followup[need_followup[email_col].isin(only_need_followup)]

    # def get_latest_need_followup_dates(self, need_followup) -> pd.DataFrame:
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
    #     date_col = self.appointments.get_col(Column.DATE)
    #     return need_followup.groupby(email_col)[date_col].max()

    # def get_student_followup(self, results_dir, archive_dir):
    #     date_col = self.appointments.get_col(Column.DATE)
    #     college_col = self.appointments.get_col(Column.STUDENT_COLLEGE)
    #     type_col = self.appointments.get_col(Column.APPOINTMENT_TYPE)
    #     email_col = self.appointments.get_col(Column.STUDENT_EMAIL)
        
    #     # filter_target_year(
    #     #     self.appointments.get_df(),
    #     #     year=self.year,
    #     #     col=date_col
    #     # )
    #     # filter_target_months(
    #     #     self.appointments.get_df(),
    #     #     months=self.months,
    #     #     col=date_col
    #     # )

    #     # valid_majors_appointment_df = filter_target_isin(
    #     #     df=self.appointments.get_df(),
    #     #     col=college_col,
    #     #     li=self.valid_majors
    #     # )

    #     # valid_majors_appointment_df[type_col] = valid_appointment_df[type_col].fillna('MissingData')
        
    #     # valid_appointment_df = valid_majors_appointment_df[
    #     #     valid_majors_appointment_df[type_col].str.startswith(self.appointment_types["include"])
    #     #     & ~(valid_majors_appointment_df[type_col].isin(self.appointment_types["disclude"]))
    #     # ]
        
    #     # invalid_appointment_df = valid_majors_appointment_df[
    #     #     ~valid_majors_appointment_df[type_col].str.startswith(self.appointment_types["include"])
    #     #                 or (valid_majors_appointment_df[type_col].isin(self.appointment_types["disclude"]))
    #     # ]

    #     latest_valid_dates = valid_appointment_df.groupby(email_col)[date_col].max()

    #     merged_df = pd.merge(
    #         left=invalid_appointment_df,
    #         right=latest_valid_dates,
    #         on=email_col,
    #         how='left',
    #         suffixes=('', '_latest_walk_in')
    #     )

    #     filtered_invalid_df = merged_df[(
    #         merged_df[date_col] >= merged_df[date_col + "_latest_walk_in"]
    #     )]

    #     latest_other_date = invalid_appointment_df.groupby(email_col)[date_col].max().reset_index(
    #         name=f'date of last non ${self.appointment_types["include"]} appointment'
    #     )
    #     duplicate_appointment_count = invalid_appointment_df.pivot_table(
    #         index=[email_col],
    #         aggfunc='size'
    #     ).reset_index(name="# of past appointments")

    #     valid_appointment_df = pd.merge(
    #         left=valid_appointment_df,
    #         right=duplicate_appointment_count,
    #         how="outer"
    #     )
    #     valid_appointment_df = pd.merge(
    #         left=valid_appointment_df,
    #         right=latest_other_date,
    #         how='outer'
    #     )

    #     # Merge enrollment data
    #     enrollment_fname = self.enrollment.get_col(Column.STUDENT_FIRST_NAME)
    #     enrollment_lname = self.enrollment.get_col(Column.STUDENT_LAST_NAME)
    #     enrollment_card_id = self.enrollment.get_col(Column.STUDENT_CARD_ID)
    #     appointments_card_id = self.appointments.get_col(Column.STUDENT_FIRST_NAME)
    #     appointments_fname = self.appointments.get_col(Column.STUDENT_LAST_NAME)
    #     appointments_lname = self.appointments.get_col(Column.STUDENT_CARD_ID)

    #     # rename card id column to match the enrollment dataframe (what we will merge on)
    #     valid_appointment_df = valid_appointment_df.rename(columns={appointments_card_id: enrollment_card_id})
    #     # merge enrollment and valid df on card id column
    #     valid_appointment_df = pd.merge(valid_appointment_df, self.enrollment.get_df()[[enrollment_card_id, enrollment_fname, enrollment_lname]], on=enrollment_card_id)
    #     # rename columns from enrollment column names to appointment column names
    #     valid_appointment_df = valid_appointment_df.rename({enrollment_fname: appointments_fname, enrollment_lname: appointments_lname, enrollment_card_id: appointments_card_id})


    #     # remove appointments where there was a followup appointment at a later date
    #     valid_appointment_df = valid_appointment_df[~(valid_appointment_df[date_col].isnull())]
        
    #     # Create a list of students that had a valid appointment and have not had an invalid appointment at a later date
    #     # filtered_invalid_df contains the entries that had an invalid appointment after the latest valid appointment
    #     only_valid = set(valid_appointment_df[email_col]) - set(filtered_invalid_df[email_col])
    #     # Now filter the valid appointments dataframe to only include students that need a followup
    #     final_df = valid_appointment_df[valid_appointment_df[email_col].isin(only_valid)]
        

    #     # Save the file(s)
    #     filename =  self.id + dt.now().strftime('%Y%m%d-%H%M%S') + ".csv"
    #     final_df.to_csv(
    #         archive_dir + "\\" + filename,
    #         index=False
    #     )

    #     final_df = remove_columns(final_df, self.remove_cols)
    #     final_df = final_df.rename(self.rename_cols)
    #     final_df = final_df[self.final_cols]

    #     final_df.to_csv(
    #         results_dir + "\\" + filename,
    #         index=False
    #     )
