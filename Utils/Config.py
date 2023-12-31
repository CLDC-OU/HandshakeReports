
import json
import logging
import os

from dotenv import load_dotenv
from datetime import datetime as dt

from Reports.Report import Report
from Reports.DataSet import DataSet, load_df
from Utils.file_utils import filter_files, get_most_recent_file


class Config():
    def __init__(self) -> None:
        try:
            with open('config.json') as json_file:
                self.config = json.load(json_file)
            logging.debug(f"Project config loaded")
        except:
            logging.error(f"WARNING! Could not find config.json")
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
            logging.debug(f"Environmental variables successfully loaded")
            self.env = True
        else:
            logging.warn(f"WARNING! There was an error loading the environmental variables. Check that the path variables are correct and the .env file exists")

    def getReports(self) -> list[Report]:
        return self.reports.getReports()
    
class FilesConfig():
    def __init__(self) -> None:
        try:
            with open('files.config.json') as json_file:
                self.config = json.load(json_file)
            logging.debug(f"Files config loaded")
        except:
            logging.warn(f"WARNING! Could not find files.config.json")
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
            rename_cols = {}
            cols = {}
            for column in file["column_names"]:
                if "map" in file["column_names"][column]:
                    rename_cols[file["column_names"][column]["map"]] = file["column_names"][column]["name"]
                cols[column] = file["column_names"][column]["name"]
                # d = None
                # if "date" in file[type]["column_names"]:
                #     d = file[type]["column_names"]["date"]["name"]
            
            logging.debug(f'Loading new {file["type"]} file...')
            valid_files = filter_files(
                file_dir=file["dir"],
                must_contain=file["must_contain"],
                file_type=".csv"
            )
            if not valid_files:
                logging.error(f'Cannot load {file["type"]} file. No valid files were found in {file["type"]["dir"]}')
                break
            else:
                logging.debug(f'Found valid file at {file["dir"]}')
            
            file_loc = get_most_recent_file(valid_files)
            logging.debug(f'Found most recent file: {file_loc}')


            self.files.append(
                DataSet(
                    file["type"],
                    file["id"], 
                    load_df(
                        file_dir=file["dir"],
                        must_contain=file["must_contain"], 
                        rename_columns=rename_cols
                        # date_col=d
                    ),
                    cols
                ))
            logging.debug(f"Loaded DataSet from file {file_loc}")
        
        return self.files

            

class ReportsConfig():
    def __init__(self) -> None:
        try:
            with open('reports.config.json') as json_file:
                self.config = json.load(json_file)
            logging.debug(f"Reports config loaded")
        except:
            logging.warn(f"WARNING! Could not find reports.config.json")
            self.config = None
        finally:
            self.reports = None
            self.files = FilesConfig()
            self.files.loadFiles()
        self.loadFiles()

    def getFiles(self) -> list[DataSet]:
        if not self.files:
            return None
        return self.files.files

    def getReports(self) -> list[Report] | None:
        return self.reports
    
    def loadFiles(self):
        self._appointments = []
        self._surveys = []
        self._enrollment = None
        self._referrals = []
        for file in self.getFiles():
            if file.type == DataSet.Type.APPOINTMENT:
                self._appointments.append(file)
            elif file.type == DataSet.Type.ENROLLMENT:
                self._enrollment = file
            elif file.type == DataSet.Type.SURVEY:
                self._surveys.append(file)
            elif file.type == DataSet.Type.REFERRAL:
                self._referrals.append(file)

    def getAppointments(self) -> list[DataSet] | None:
        return self._appointments
    def getEnrollment(self) -> DataSet | None:
        return self._enrollment
    def getSurveyResults(self) -> list[DataSet] | None:
        return self._surveys
    def getReferrals(self) -> list[DataSet] | None:
        return self._referrals
    def getSurveyByID(self, survey_id) -> DataSet | None:
        for survey in self.getSurveyResults():
            if survey.get_id() == survey_id:
                return survey
        return None

    def loadReports(self) -> list[Report] | None:
        if not self.config:
            return None
        
        self.reports = []

        reports = self.config["reports"]

        report_index = 0
        for report in reports:
            report_index += 1
            error = False
            if "type" not in report:
                logging.error(f"ERROR! \"type\" key not present in reports.config.json at index {report_index}")
                error = True
            if "file_prefix" not in report:
                logging.error(f"ERROR! \"file_prefix\" key not present in reports.config.json at index {report_index}")
                error = True
            if "results_dir" not in report:
                logging.error(f"ERROR! \"results_dir\" key not present in reports.config.json at index {report_index}")
                error = True
            if error:
                logging.error(f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
                break
            type = report["type"]
            if type == Report.Type.SURVEY_RESULTS.value:
                for appointment in self.getAppointments():
                    if "survey_id" not in report:
                        logging.error(f"ERROR! \"survey_id\" key not present for {type} report in reports.config.json at index {report_index}")
                        break

                    survey_id = report["survey_id"]
                    survey = self.getSurveyByID(survey_id)
                    if survey is None:
                        logging.error(f"ERROR! No survey was found with the ID {survey_id}")
                        break
                    else:
                        logging.info(f"Found survey with id {survey_id}")
                    
                    error = False
                    if "day_range" not in report:
                        logging.error(f"ERROR! \"day_range\" key not present for {type} report in reports.config.json at index {report_index}")
                        error = True
                    if "target_year" not in report:
                        report["target_year"] = None
                        logging.warn(f"WARNING! \"target_year\" key not present for {type} report in reports.config.json at index {report_index}. Setting to default including all years")
                    else:
                        if report["target_year"] == "" or report["target_year"] == []:
                            report["target_year"] = None
                    if "target_months" not in report:
                        logging.warn(f"WARNING! \"target_months\" key not present for {type} in reports.config.json at index {report_index}. Setting to default including all months")
                        report["target_months"] = None
                    else:
                        if report["target_months"] == "" or report["target_months"] == []:
                            report["target_months"] = None
                    if "emails" not in report:
                        logging.warn(f"WARNING! \"emails\" key not present for {type} in reports.config.json at index {report_index}. Setting to default including all emails")
                        report["emails"] = None
                    else:
                        if report["emails"] == "" or report["emails"] == []:
                            report["emails"] = None
                    if error:
                        logging.error(f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
                        break

                    conf = {
                        "type": report["type"],
                        "file_prefix": report["file_prefix"],
                        "appointments": appointment.deep_copy(),
                        "survey_results": survey.deep_copy(),
                        "day_range": report["day_range"],
                        "year": report["target_year"],
                        "months": report["target_months"], 
                        "emails": report["emails"],
                        "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                        "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                        "final_cols": report["final_cols"] if "final_cols" in report else None,
                        "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                        "results_dir": report["results_dir"] if "results_dir" in report else None
                    }
                    self.reports.append(Report(conf))
                    
            if type == Report.Type.FOLLOWUP.value:
                for appointment in self.getAppointments():
                    error = False
                    if "valid_schools" not in report:
                        logging.warn(f"WARNING! \"valid_schools\" key not present for {type} report in reports.config.json at index {report_index}. Setting to default including all schools")
                        report["valid_schools"] = None
                    else:
                        if report["valid_schools"] == "" or report["valid_schools"] == []:
                            report["valid_schools"] = None
                    if "target_year" not in report:
                        logging.warn(f"WARNING! \"target_year\" key not present for {type} report in reports.config.json at index {report_index}. Setting to default including all years")
                        report["target_year"] == None
                    else:
                        if report["target_year"] == "" or report["target_year"] == []:
                            report["target_year"] = None
                    if "target_months" not in report:
                        logging.warn(f"WARNING! \"target_months\" key not present for {type} in reports.config.json at index {report_index}. Setting to default including all months")
                        report["target_months"] = None
                    else:
                        if report["target_months"] == "" or report["target_months"] == []:
                            report["target_months"] = None
                    if "appointment_types" not in report:
                        logging.error(f"WARNING! \"appointment_types\" key not present for {type} in reports.config.json at index {report_index}")
                        error = True
                    if "followup_types" not in report:
                        logging.error(f"WARNING! \"followup_types\" key not present for {type} in reports.config.json at index {report_index}")
                        error = True
                    if error:
                        logging.error(f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
                        break
                    conf = {
                        "type": report["type"],
                        "file_prefix": report["file_prefix"],
                        "appointments": appointment.deep_copy(),
                        "valid_schools": report["valid_schools"],
                        "year": report["target_year"],
                        "months": report["target_months"],
                        "appointment_types": report["appointment_types"], 
                        "followup_types": report["followup_types"],
                        "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                        "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                        "final_cols": report["final_cols"] if "final_cols" in report else None,
                        "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                        "results_dir": report["results_dir"] if "results_dir" in report else None,
                    }
                    self.reports.append(Report(conf))
            if type == Report.Type.REFERRALS.value:
                for referral in self.getReferrals():
                    for appointment in self.getAppointments():
                        error = False
                        if "valid_appointments" not in report:
                            logging.error(f"ERROR! \"valid_appointments\" key not present for {type} report in reports.config.json at index {report_index}")
                            error = True
                        if error:
                            logging.error(f"ERROR! Report {report_index} could not be loaded due to missing essential keys")
                            break
                        conf = {
                            "type": report["type"],
                            "file_prefix": report["file_prefix"],
                            "referrals": referral.deep_copy(),
                            "appointments": appointment.deep_copy(),
                            "valid_appointments": report["valid_appointments"],
                            "remove_cols": report["remove_cols"] if "remove_cols" in report else None, 
                            "rename_cols": report["rename_cols"] if "rename_cols" in report else None, 
                            "final_cols": report["final_cols"] if "final_cols" in report else None,
                            "enrollment": self.getEnrollment().deep_copy(),
                            "merge_enrollment": report["merge_enrollment"] if "merge_enrollment" in report else None,
                            "archive_dir": report["archive_dir"] if "archive_dir" in report else None,
                            "results_dir": report["results_dir"] if "results_dir" in report else None,
                        }
                        self.reports.append(Report(conf))
        return self.reports
