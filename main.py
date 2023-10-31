import pandas as pd
from Reports.DataSet import DataSet, load_df
from Reports.Report import Report
from Utils.file_utils import filter_files, get_most_recent_file
from Utils.utils import config
from datetime import datetime as dt


class Driver():
    def __init__(self) -> None:
        self.files = []
        self.reports = []
    
    def run(self):
        self._load_files()
        self._load_reports()
        self._run_reports()

    def _load_files(self):
        self.files = []
        
        files = config["files"]
        
        for file in files:
            for type in file:
                rename_cols = {}
                cols = {}
                for column in file[type]["column_names"]:
                    if "map" in file[type]["column_names"][column]:
                        rename_cols[file[type]["column_names"][column]["map"]] = file[type]["column_names"][column]["name"]
                    cols[column] = file[type]["column_names"][column]["name"]
                    d = None
                    if "date" in file[type]["column_names"]:
                        d = file[type]["column_names"]["date"]["name"]
                print(f"[Driver {dt.now()}] Adding new {type} file")
                self.files.append(
                    DataSet(
                        type,
                        file[type]["id"], 
                        load_df(
                            file_dir=file[type]["dir"],
                            must_contain=file[type]["must_contain"], 
                            rename_columns=rename_cols
                            # date_col=d
                        ),
                        cols
                ))
                loc = get_most_recent_file(filter_files(
                    file_dir=file[type]["dir"],
                    must_contain=file[type]["must_contain"],
                    file_type=".csv"
                ))
                print(f"[Driver {dt.now()}] Loaded DataSet from file {loc}")

    def _load_reports(self):
        self.reports = []

        reports = config["reports"]

        appointments = []
        surveys = []
        enrollment = None
        referrals = []
        for file in self.files:
            if file.type == DataSet.Type.APPOINTMENT:
                appointments.append(file)
            elif file.type == DataSet.Type.ENROLLMENT:
                enrollment = file
            elif file.type == DataSet.Type.SURVEY:
                surveys.append(file)
            elif file.type == DataSet.Type.REFERRAL:
                referrals.append(file)

        for report in reports:
            type = report["type"]
            if type == Report.Type.SURVEY_RESULTS.value:
                for appointment in appointments:
                    for survey in surveys:
                        conf = {
                            "type": report["type"],
                            "file_prefix": report["file_prefix"],
                            "appointments": appointment.deep_copy(),
                            "survey_results": survey.deep_copy(),
                            "day_range": report["day_range"] if "day_range" in report else None,
                            "year": report["target_year"] if "target_year" in report else None, 
                            "months": report["target_months"] if "target_months" in report else None, 
                            "emails": report["emails"] if "emails" in report else None, 
                            "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                            "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                            "final_cols": report["final_cols"] if "final_cols" in report else None,
                            "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                            "results_dir": report["results_dir"] if "results_dir" in report else None,
                        }
                        self.reports.append(Report(conf))
            if type == Report.Type.FOLLOWUP.value:
                for appointment in appointments:
                    conf = {
                        "type": report["type"],
                        "file_prefix": report["file_prefix"],
                        "appointments": appointment.deep_copy(),
                        "valid_schools": report["valid_schools"] if "valid_schools" in report else None,
                        "year": report["target_year"] if "target_year" in report else None, 
                        "months": report["target_months"] if "target_months" in report else None, 
                        "appointment_types": report["appointment_types"] if "appointment_types" in report else None, 
                        "followup_types": report["valid_followup"] if "valid_followup" in report else None,
                        "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                        "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                        "final_cols": report["final_cols"] if "final_cols" in report else None,
                        "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                        "results_dir": report["results_dir"] if "results_dir" in report else None,
                    }
                    self.reports.append(Report(conf))
            if type == Report.Type.REFERRALS.value:
                for referral in referrals:
                    for appointment in appointments:
                        conf = {
                            "type": report["type"],
                            "file_prefix": report["file_prefix"],
                            "referrals": referral.deep_copy(),
                            "appointments": appointment.deep_copy(),
                            "valid_appointments": report["valid_appointments"] if "valid_appointments" in report else None,
                            "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                            "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                            "final_cols": report["final_cols"] if "final_cols" in report else None,
                            "enrollment": enrollment.deep_copy(),
                            "merge_enrollment": report["merge_enrollment"] if "merge_enrollment" in report else None,
                            "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                            "results_dir": report["results_dir"] if "results_dir" in report else None,
                        }
                        self.reports.append(Report(conf))

    def _run_reports(self):
        if not self.reports:
            return False
        for report in self.reports:
            report.run_report()
            print(f"[Driver {dt.now()}] Successfully ran {report.type} report")
            report.save_archive()
            print(f"[Driver {dt.now()}] Saved archive of {report.type} report to {report.archive_dir}")
            report.save_results()
            print(f"[Driver {dt.now()}] Saved results of {report.type} report to {report.results_dir}")
        return True
            
            
Driver().run()