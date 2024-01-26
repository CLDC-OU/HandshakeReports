import logging

from src.dataset.dataset import DataSet
from src.dataset.appointment import AppointmentDataSet
from src.dataset.enrollment import EnrollmentDataSet
from src.dataset.referral import ReferralDataSet
from src.dataset.survey import SurveyDataSet
from src.utils.df_utils import load_df
from src.utils.file_utils import dir_format, filter_files, get_most_recent_file
from src.config.config import Config

FILES_CONFIG_FILE = "files.config.json"


class FilesConfig(Config):
    def __init__(self, config_file: str = FILES_CONFIG_FILE) -> None:
        super().__init__(config_file)
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
            raise ValueError("Cannot load config file")
        return self.load_files() is not None

    def load_files(self) -> list[DataSet] | None:
        logging.debug("Loading files...")
        if not self.config:
            self.files = []
            return None

        self.files = []
        files = self.config["files"]
        for file in files:
            rename_cols, cols = FilesConfig.map_column_config(file["column_names"])
            message = f'Loading new {file["type"]} file...'
            logging.debug(f'{message}\n\t{file}')
            print(message)
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
            message = f'\tFound most recent {file["type"]} file: {file_loc}'
            logging.debug(message)
            print(message)

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
                message = f'ERROR: Cannot load {file["type"]} file. Invalid type.'
                logging.error(message)
                print(message)
                break
            self.files.append(dataset)
            message = f'\tLoaded {dataset.__class__.__name__} from file: {file_loc}'
            logging.debug(message)
            print(message)

        return self.files
