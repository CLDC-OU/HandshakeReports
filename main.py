
from datetime import datetime as dt
import logging

logfile = f"logs/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG, filemode='w', format='%(levelname)s:%(asctime)s:[%(module)s] %(message)s')
logging.info("Log started")

from Utils.Config import Config


class Driver():
    def __init__(self) -> None:
        self._config = Config()
        

    def run(self):
        self._getReports().loadReports()
        self._run_reports()
    
    def _getReports(self):
        return self._config.reports
    
    def _run_reports(self):
        if not self._getReports():
            return False
        for report in self._getReports().reports:
            report.run_report()
            
            logging.info(f"Successfully ran {report.type} report")
            report.save_archive()
            logging.info(f"Saved archive of {report.type} report to {report.archive_dir}")
            report.save_results()
            logging.info(f"Saved results of {report.type} report to {report.results_dir}")
        return True

Driver().run()