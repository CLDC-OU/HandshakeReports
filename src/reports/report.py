import logging
import pandas as pd
from colorama import Style, Fore

from src.utils.df_utils import remove_columns
from datetime import datetime as dt


class Report:
    # class Type(Enum):
    #     SURVEY_RESULTS = 'survey_results'
    #     FOLLOWUP = 'followup'
    #     REFERRALS = 'referrals'

    #     def __eq__(self, __value: object) -> bool:
    #         return self.value.__eq__(__value)

    def __init__(
            self,
            file_prefix: str,
            results_dir: str,
            report: "Report",
            archive_dir: str | None = None,
            remove_cols: list[str] | None = None,
            rename_cols: dict | None = None,
            final_cols: list[str] | None = None
    ) -> None:
        self.file_prefix = file_prefix
        if not results_dir:
            raise ValueError("results_dir must be a valid directory")
        self.results_dir = results_dir
        self.report = report
        self.archive_dir = archive_dir
        self.remove_cols = remove_cols
        self.rename_cols = rename_cols
        self.final_cols = final_cols
        self.results = pd.DataFrame()

    def get_class_name(self) -> str:
        return self.__class__.__name__

    def run_report(self) -> None:
        logging.debug(f"Running {self.report.get_class_name()} report")
        print(f'{Fore.CYAN}Running {Fore.LIGHTYELLOW_EX}{self.report.get_class_name()}{Fore.CYAN} report{Style.RESET_ALL}')
        self.report.run_report()
        self.results = self.report.get_results()
        if self.results is None or self.results.empty:
            logging.debug(f"\tRan {self.report.get_class_name()} report, but got no results.")
            print(f'\t{Fore.YELLOW}Ran {Fore.LIGHTYELLOW_EX}{self.report.get_class_name()} {Fore.YELLOW}report, but got no results.{Style.RESET_ALL}')
        else:
            logging.debug(f"\tSuccessfully ran {self.report.get_class_name()} report with {len(self.results)} results")
            print(f'\t{Fore.GREEN}Successfully ran {Fore.LIGHTYELLOW_EX}{self.report.get_class_name()} {Fore.GREEN}report with {Fore.LIGHTMAGENTA_EX}{len(self.results)} {Fore.GREEN}results{Style.RESET_ALL}')

    def get_results(self) -> pd.DataFrame | None:
        return None

    @property
    def results(self) -> pd.DataFrame | None:
        if not isinstance(self._results, pd.DataFrame):
            logging.warning(f"Invalid results type {type(self._results)}. Using None")
            print(f'{Fore.LIGHTBLACK_EX}Invalid {Fore.LIGHTWHITE_EX}results {Fore.LIGHTBLACK_EX}type {type(self._results)}. Using {Fore.LIGHTWHITE_EX}None{Style.RESET_ALL}')
            return None
        return self._results

    @results.setter
    def results(self, value: pd.DataFrame | None) -> None:
        self._results = value

    @property
    def rename_cols(self) -> dict[str, str] | None:
        if not isinstance(self._rename_cols, dict):
            logging.warning(f"Invalid rename_cols type {type(self._rename_cols)}. Using None")
            print(f'{Fore.LIGHTBLACK_EX}Invalid {Fore.LIGHTWHITE_EX}rename_cols {Fore.LIGHTBLACK_EX}type {type(self._rename_cols)}. Using {Fore.LIGHTWHITE_EX}None{Style.RESET_ALL}')
            return None
        return self._rename_cols

    @rename_cols.setter
    def rename_cols(self, value: dict[str, str] | None) -> None:
        if not isinstance(value, dict):
            logging.warning(f"Invalid rename_cols type {type(value)}. Using None")
            print(f'{Fore.LIGHTBLACK_EX}Invalid {Fore.LIGHTWHITE_EX}rename_cols {Fore.LIGHTBLACK_EX}type {type(value)}. Using {Fore.LIGHTWHITE_EX}None{Style.RESET_ALL}')
            self._rename_cols = None
        self._rename_cols = value

    def get_filename(self) -> str:
        return self.file_prefix + dt.now().strftime('%Y%m%d-%H%M%S') + '.csv'

    def save_archive(self):
        if not self.archive_dir:
            logging.debug("No archive directory specified. Skipping archive")
            print(f'{Fore.LIGHTBLACK_EX}No archive directory specified. Skipping archive{Style.RESET_ALL}')
            return
        if self.results is None or self.results.empty:
            logging.warning("No results to archive. Either this report did not have run correctly or the results were empty")
            print(f'{Fore.LIGHTBLACK_EX}No results to archive. Either this report did not have run correctly or the results were empty{Style.RESET_ALL}')
            return
        self.results.to_csv(self.archive_dir + "\\" + self.get_filename(), index=False)
        logging.debug(f"\tSaved archive of {self.report.get_class_name()} to {self.results_dir}\\{self.get_filename()}")
        print(f'\t{Fore.LIGHTGREEN_EX}Saved archive of {Fore.LIGHTYELLOW_EX}{self.report.get_class_name()} {Fore.LIGHTGREEN_EX}to {Fore.LIGHTBLACK_EX}{self.results_dir}\\{self.get_filename()}{Style.RESET_ALL}')

    def save_results(self):
        if self.results is None or self.results.empty:
            logging.warning("No results to save. Either this report did not have run correctly or the results were empty")
            print(f'{Fore.LIGHTBLACK_EX}No results to save. Either this report did not have run correctly or the results were empty{Style.RESET_ALL}')
            return

        if self.remove_cols:
            self.results = remove_columns(self.results, self.remove_cols)
        if self.rename_cols:
            self.results = self.results.rename(columns=self.rename_cols)
        if self.final_cols:
            self.results = self.results[self.final_cols]

        self.results.to_csv(self.results_dir + "\\" + self.get_filename())
        logging.debug(f"\tSaved results of {self.report.get_class_name()} to {self.results_dir}\\{self.get_filename()}")
        print(f'\t{Fore.LIGHTGREEN_EX}Saved results of {Fore.LIGHTYELLOW_EX}{self.report.get_class_name()} {Fore.LIGHTGREEN_EX}to {Fore.LIGHTBLACK_EX}{self.results_dir}\\{self.get_filename()}{Style.RESET_ALL}')
