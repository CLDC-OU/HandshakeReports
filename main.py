from datetime import datetime as dt

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
            print(f"[Driver {dt.now()}] Successfully ran {report.type} report")
            report.save_archive()
            print(f"[Driver {dt.now()}] Saved archive of {report.type} report to {report.archive_dir}")
            report.save_results()
            print(f"[Driver {dt.now()}] Saved results of {report.type} report to {report.results_dir}")
        return True

Driver().run()