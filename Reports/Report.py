from enum import Enum

import pandas as pd
from .Followup import Followup
from .Referrals import Referrals
from .SurveyResults import SurveyResults
from Utils.df_utils import remove_columns
from datetime import datetime as dt


class Report:
    class Type(Enum):
        SURVEY_RESULTS = 'survey_results'
        FOLLOWUP = 'followup'
        REFERRALS = 'referrals'
        def __eq__(self, __value: object) -> bool:
            return self.value.__eq__(__value)
    
    def __init__(self, config:dict) -> None:
        self.type = config["type"]
        self.file_prefix = config["file_prefix"]
        self.archive_dir = config["archive_dir"]
        self.results_dir = config["results_dir"]
        if config["type"] == Report.Type.SURVEY_RESULTS:
            print(f"[Report {dt.now()}] Creating new SurveyResults Report")
            self.report = SurveyResults(config["appointments"], config["survey_results"], config["day_range"], config["year"], config["months"], config["emails"], config["remove_cols"])
            self.results = None
        elif config["type"] == Report.Type.FOLLOWUP:
            print(f"[Report {dt.now()}] Creating new Followup Report")
            self.report = Followup(config["appointments"], config["enrollment"], config["valid_schools"], config["year"], config["months"], config["appointment_types"], config["followup_types"], config["remove_cols"], config["rename_cols"], config["final_cols"])
            self.results = None
        elif config["type"] == Report.Type.REFERRALS:
            print(f"[Report {dt.now()}] Creating new Referrals Report")
            self.report = Referrals(config["referrals"], config["appointments"], config["valid_appointments"], config["rename_cols"], config["final_cols"], config["enrollment"], config["merge_enrollment"])
            self.results = None
        else:
            print(f"[Report {dt.now()}] Invalid Report Type {config['type']}")
            self.report = None
            self.results = pd.DataFrame(None)
    
    def run_report(self) -> None:
        print(f"[Report {dt.now()}] Running report for {self.type}")
        self.report.run_report()
        self.results = self.report.get_results()
    
    def get_results(self) -> pd.DataFrame | None:
        return self.results

    def get_filename(self) -> str:
        return self.file_prefix + dt.now().strftime('%Y%m%d-%H%M%S') + '.csv'
    
    def save_archive(self):
        self.results.to_csv(self.archive_dir + "\\" + self.get_filename(), index=False)

    def save_results(self):
        if self.results.empty:
            return None

        if self.report.remove_cols:
            self.results = remove_columns(self.results, self.report.remove_cols)
        if self.report.rename_cols:
            # print(self.report.rename_cols)
            self.results = self.results.rename(columns=self.report.rename_cols)
        if self.report.final_cols:
            self.results = self.results[self.report.final_cols]

        self.results.to_csv(self.results_dir + "\\" + self.get_filename())

    # def __init__(self, type, report:SurveyResults|Followup) -> None:
    #     self.type = type
    #     self.report = report
    # def __init_subclass__(cls, config) -> None:
    #     cls.type = config["type"]
    #     if config["type"] == ReportType.SURVEY_RESULTS:
    #         cls.report = SurveyResults(config["file_prefix"], config["appointments"], config["survey_results"], config["target_year"], config["target_months"], config["emails"], config["remove_cols"])
    #     elif config["type"] == ReportType.FOLLOWUP:
    #         cls.report = Followup(config["file_prefix"], config["appointments"], config["valid_majors"], config["target_year"], config["target_months"], config["remove_cols"], config["rename_cols"], config["final_cols"])
    #     else:
    #         cls.report = None

