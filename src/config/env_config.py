import logging
import os
from dotenv import load_dotenv

from src.config.config import Config

DEFAULT_ENV_PATH = ".env"


class EnvConfig(Config):
    def __init__(self, config_file: str = "config.json", use_env: bool = True) -> None:
        self._use_env = use_env
        self._env_path = DEFAULT_ENV_PATH
        self.env = False
        super().__init__(config_file)

    def set_env_path(self, env_path: str) -> None:
        self._env_path = env_path

    def load_config(self):
        if self._use_env:
            self._load_env()

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

    def _load_env(self) -> None:
        if load_dotenv(dotenv_path=self._env_path, override=True):
            logging.debug("Environmental variables successfully loaded")
            self.env = True
        else:
            logging.warning(
                "WARNING! There was an error loading the environmental variables. Check that the path variables are "
                "correct and the .env file exists")
