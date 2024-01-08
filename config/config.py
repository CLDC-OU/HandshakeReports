import json
import logging
import os

from dotenv import load_dotenv

DEFAULT_ENV_PATH = ".env"


class Config:
    def __init__(self, config_file: str = "config.json", use_env: bool = True) -> None:
        self._use_env = use_env
        self._env_dir = DEFAULT_ENV_PATH
        self.env = False

        self._config_file = config_file
        self.config = None

    def set_env_path(self, env_path: str) -> None:
        self._env_path = env_path

    def load_config(self):
        if self._use_env:
            self._load_env()
        return self._open_config()

    def get_username(self) -> str | None:
        if self.env:
            return os.getenv("HS_USERNAME")
        return None

    def get_password(self) -> str | None:
        if self.env:
            return os.getenv("HS_PASSWORD")
        return None

    def is_institutional(self) -> bool:
        if self.env:
            return os.getenv("INSTITUTIONAL_EMAIL") == "TRUE"
        return False

    def _open_config(self):
        try:
            with open(self._config_file) as json_file:
                self.config = json.load(json_file)
            if self.config is None:
                raise Exception("Config file is empty")
            logging.debug("Project config loaded")
            return True
        except Exception as e:
            logging.error(f"WARNING! Could not find {self._config_file} {str(e)}")
        self.config = None
        return False

    def _load_env(self) -> None:
        if load_dotenv(dotenv_path=self._env_path, override=True):
            logging.debug("Environmental variables successfully loaded")
            self.env = True
        else:
            logging.warning(
                "WARNING! There was an error loading the environmental variables. Check that the path variables are "
                "correct and the .env file exists")
