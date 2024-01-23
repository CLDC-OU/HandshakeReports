import json
import logging

DEFAULT_ENV_PATH = ".env"


class Config:
    def __init__(self, config_file: str = "config.json") -> None:
        self._config_file = config_file
        self.config = None

    def load_config(self):
        return self._open_config()

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
