import unittest
from unittest.mock import patch
from src.config.env_config import EnvConfig


class TestEnvConfig(unittest.TestCase):
    def setUp(self):
        self.config = EnvConfig()

    def test_set_env_path(self):
        self.config.set_env_path("/path/to/env")
        self.assertEqual(self.config._env_path, "/path/to/env")

    @patch("src.config.env_config.load_dotenv")
    def test_load_config_with_env(self, mock_load_dotenv):
        self.config._use_env = True
        mock_load_dotenv.return_value = True
        self.config._load_env()
        self.assertTrue(self.config.env)

    @patch("src.config.env_config.load_dotenv")
    def test_load_config_without_env(self, mock_load_dotenv):
        self.config._use_env = False
        mock_load_dotenv.return_value = False
        self.config._load_env()
        self.assertFalse(self.config.env)

    @patch("os.getenv")
    def test_get_username_with_env(self, mock_getenv):
        self.config.env = True
        mock_getenv.return_value = "test_username"
        self.assertEqual(self.config.get_username(), "test_username")

    @patch("os.getenv")
    def test_get_username_without_env(self, mock_getenv):
        self.config.env = False
        self.assertIsNone(self.config.get_username())

    @patch("os.getenv")
    def test_get_password_with_env(self, mock_getenv):
        self.config.env = True
        mock_getenv.return_value = "test_password"
        self.assertEqual(self.config.get_password(), "test_password")

    @patch("os.getenv")
    def test_get_password_without_env(self, mock_getenv):
        self.config.env = False
        self.assertIsNone(self.config.get_password())

    @patch("os.getenv")
    def test_is_institutional_with_env(self, mock_getenv):
        self.config.env = True
        mock_getenv.return_value = "TRUE"
        self.assertTrue(self.config.is_institutional())

    @patch("os.getenv")
    def test_is_institutional_without_env(self, mock_getenv):
        self.config.env = False
        self.assertFalse(self.config.is_institutional())
