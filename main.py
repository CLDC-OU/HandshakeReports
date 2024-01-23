
from datetime import datetime as dt
import logging

logfile = f"logs/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG, filemode='w', format='%(levelname)s:%(asctime)s:[%(module)s] %(message)s')
logging.info("Log started")

from Utils.Config import Config
from Reports.Report import Report

class Driver():
    def __init__(self) -> None:
        self._config = Config()
        

    def run(self):
        self._config.reports.loadReports()
        self._run_reports()
    
    def _getReports(self) -> list[Report]:
    
        return self._reports_config.get_reports()
    def _run_reports(self):
        if not self._getReports():
            return False
        for report in self._getReports():
            
            report.run_report()

            logging.info(f"Successfully ran {report.__class__} report")
            report.save_archive()
            logging.info(f"Saved archive of {report.__class__} report to {report.archive_dir}")
            report.save_results()
            logging.info(f"Saved results of {report.__class__} report to {report.results_dir}")
        return True

Driver().run()