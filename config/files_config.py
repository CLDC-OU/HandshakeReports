import logging

from dataset.dataset import DataSet
from dataset.appointment import AppointmentDataSet
from dataset.enrollment import EnrollmentDataSet
from dataset.referral import ReferralDataSet
from dataset.survey import SurveyDataSet
from Utils.df_utils import load_df
from Utils.file_utils import dir_format, filter_files, get_most_recent_file
from config.config import Config

FILES_CONFIG_FILE = "files.config.json"


class FilesConfig(Config):
    def __init__(self, config_file: str = FILES_CONFIG_FILE) -> None:
        super().__init__(config_file, False)
        self._files = []
        self._config = None

    @property
    def files(self) -> list[DataSet]:
        return self._files

    @files.setter
    def files(self, files: list[DataSet]) -> None:
        if not isinstance(files, list):
            raise ValueError("files must be a valid list of DataSets")
        self._files = files

    @property
    def config(self) -> dict | None:
        return self._config

    @config.setter
    def config(self, config: dict | None) -> None:
        self._config = config

    @staticmethod
    def map_column_config(column_config: dict) -> tuple[dict, dict]:
        rename_cols = {}
        cols = {}
        for column in column_config:
            if "map" in column_config[column]:
                rename_cols[column_config[column]["map"]] = column_config[column]["name"]
            cols[column] = column_config[column]["name"]
        return rename_cols, cols

    def load_config(self) -> bool:
        if not self._open_config():
            return False
        return self.load_files() is not None

    def load_files(self) -> list[DataSet] | None:
        if not self.config:
            self.files = []
            return None

        self.files = []
        files = self.config["files"]
        for file in files:
            rename_cols, cols = FilesConfig.map_column_config(file["column_names"])
            logging.debug(f'Loading new {file["type"]} file...')
            print(f'Loading new {file["type"]} file...')
            file["dir"] = dir_format(file["dir"])
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

            dataset = None
            dataset_config = (
                file["id"],
                load_df(
                    file_dir=file["dir"],
                    must_contain=file["must_contain"],
                    rename_columns=rename_cols
                ),
                cols
            )
            if file["type"] == AppointmentDataSet.type_name:
                dataset = AppointmentDataSet(*dataset_config)
            elif file["type"] == EnrollmentDataSet.type_name:
                dataset = EnrollmentDataSet(*dataset_config)
            elif file["type"] == ReferralDataSet.type_name:
                dataset = ReferralDataSet(*dataset_config)
            elif file["type"] == SurveyDataSet.type_name:
                dataset = SurveyDataSet(*dataset_config)
            else:
                logging.error(f'Cannot load {file["type"]} file. Invalid type.')
                break
            self.files.append(dataset)
            logging.debug(f"Loaded DataSet from file {file_loc}")

        return self.files
