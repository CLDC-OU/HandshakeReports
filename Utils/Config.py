
import json
import os

from dotenv import load_dotenv
from datetime import datetime as dt
from Reports.Report import Report

from Reports.DataSet import DataSet, load_df
from file_utils import filter_files, get_most_recent_file


class Config():
    def __init__(self) -> None:
        try:
            with open('config.json') as json_file:
                self.config = json.load(json_file)
            print(f"[Config {dt.now()}] Project config loaded")
        except:
            print(f"WARNING! [Config {dt.now()}] Could not find config.json")
            self.config = None
        self.reports = ReportsConfig()
        self.env = False
        self._load_env()
    
    def get_username(self):
        if self.env:
            return os.getenv("HS_USERNAME")
    def get_password(self):
        if self.env:
            return os.getenv("HS_PASSWORD")
    def is_institutional(self):
        if self.env:
            return os.getenv("INSTITUTIONAL_EMAIL") == "TRUE"

    def _load_env(self):
        if load_dotenv():
            print(f"[Config {dt.now()}] Environmental variables successfully loaded")
            self.env = True
        else:
            print(f"WARNING! [Config {dt.now()}] There was an error loading the environmental variables. Check that the path variables are correct and the .env file exists")

    
class FilesConfig():
    def __init__(self) -> None:
        try:
            with open('files.config.json') as json_file:
                self.config = json.load(json_file)
            print(f"[FilesConfig {dt.now()}] Files config loaded")
        except:
            print(f"WARNING! [FilesConfig {dt.now()}] Could not find files.config.json")
            self.config = None
        finally:
            self.files = None
    
    def loadFiles(self) -> list[DataSet] | None:
        if not self.config:
            self.files = None
            return None
        
        self.files = []
        files = self.config["files"]
        
        for file in files:
            for type in file:
                rename_cols = {}
                cols = {}
                for column in file[type]["column_names"]:
                    if "map" in file[type]["column_names"][column]:
                        rename_cols[file[type]["column_names"][column]["map"]] = file[type]["column_names"][column]["name"]
                    cols[column] = file[type]["column_names"][column]["name"]
                    # d = None
                    # if "date" in file[type]["column_names"]:
                    #     d = file[type]["column_names"]["date"]["name"]
                
                print(f"[FilesConfig {dt.now()}] Loaded new {type} file")
                valid_files = filter_files(
                    file_dir=file[type]["dir"],
                    must_contain=file[type]["must_contain"],
                    file_type=".csv"
                )
                if not valid_files:
                    print(f'[FilesConfig {dt.now()}] Cannot load {type} file. No valid files were found in {file[type]["dir"]}')
                    break
                else:
                    print(f'[FilesConfig {dt.now()}] Found valid file at {file[type]["dir"]}')
                
                file_loc = get_most_recent_file(valid_files)
                print(f'[FilesConfig {dt.now()}] Found most recent file: {file_loc}')


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
                print(f"[FilesConfig {dt.now()}] Loaded DataSet from file {file_loc}")
        
        return self.files

            

class ReportsConfig():
    def __init__(self) -> None:
        try:
            with open('reports.config.json') as json_file:
                self.config = json.load(json_file)
            print(f"[ReportsConfig {dt.now()}] Reports config loaded")
        except:
            print(f"WARNING! [ReportsConfig {dt.now()}] Could not find reports.config.json")
            self.config = None
        finally:
            self.reports = None
            self.files = FilesConfig()
    
    def loadReports(self) -> list[Report] | None:
        if not self.config:
            return None
        
        self.reports = []

        reports = self.config["reports"]

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

        report_index = 0
        for report in reports:
            report_index += 1
            error = False
            if "type" not in report:
                print(f"ERROR! [ReportsConfig {dt.now()}] \"type\" key not present in reports.config.json at index {report_index}")
                error = True
            if "file_prefix" not in report:
                print(f"ERROR! [ReportsConfig {dt.now()}] \"file_prefix\" key not present in reports.config.json at index {report_index}")
                error = True
            if "results_dir" not in report:
                print(f"ERROR! [ReportsConfig {dt.now()}] \"results_dir\" key not present in reports.config.json at index {report_index}")
                error = True
            if error:
                print(f"ERROR! [ReportsConfig {dt.now()}] Report {report_index} could not be loaded due to missing essential keys")
                break
            type = report["type"]
            if type == Report.Type.SURVEY_RESULTS.value:
                for appointment in appointments:
                    for survey in surveys:
                        error = False
                        if "day_range" not in report:
                            print(f"ERROR! [ReportsConfig {dt.now()}] \"day_range\" key not present for {type} report in reports.config.json at index {report_index}")
                            error = True
                        if "year" not in report:
                            print(f"WARNING! [ReportsConfig {dt.now()}] \"year\" key not present for {type} report in reports.config.json at index {report_index}")
                            error = True
                        if "months" not in report:
                            print(f"WARNING! [ReportsConfig {dt.now()}] \"months\" key not present for {type} in reports.config.json at index {report_index}")
                            error = True
                        if "emails" not in report:
                            print(f"WARNING! [ReportsConfig {dt.now()}] \"emails\" key not present for {type} in reports.config.json at index {report_index}")
                            error = True
                        if error:
                            print(f"WARNING! [ReportsConfig {dt.now()}] Report {report_index} could not be loaded due to missing essential keys")
                            break

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
                    error = False
                    if "valid_schools" not in report:
                        print(f"ERROR! [ReportsConfig {dt.now()}] \"valid_schools\" key not present for {type} report in reports.config.json at index {report_index}")
                        error = True
                    if "year" not in report:
                        print(f"WARNING! [ReportsConfig {dt.now()}] \"year\" key not present for {type} report in reports.config.json at index {report_index}")
                        error = True
                    if "months" not in report:
                        print(f"WARNING! [ReportsConfig {dt.now()}] \"months\" key not present for {type} in reports.config.json at index {report_index}")
                        error = True
                    if "appointment_types" not in report:
                        print(f"WARNING! [ReportsConfig {dt.now()}] \"appointment_types\" key not present for {type} in reports.config.json at index {report_index}")
                        error = True
                    if "followup_types" not in report:
                        print(f"WARNING! [ReportsConfig {dt.now()}] \"followup_types\" key not present for {type} in reports.config.json at index {report_index}")
                        error = True
                    if error:
                        print(f"WARNING! [ReportsConfig {dt.now()}] Report {report_index} could not be loaded due to missing essential keys")
                        break
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
                        error = False
                        if "valid_appointments" not in report:
                            print(f"ERROR! [ReportsConfig {dt.now()}] \"valid_schools\" key not present for {type} report in reports.config.json at index {report_index}")
                            error = True
                        if error:
                            print(f"WARNING! [ReportsConfig {dt.now()}] Report {report_index} could not be loaded due to missing essential keys")
                            break
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
        return self.reports

print(Config().is_institutional())