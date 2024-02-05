import unittest
from unittest.mock import patch
from src.config.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_file = "tests/test_files/test_config.json"
        self.config = Config(self.config_file)

    def test_open_config(self):
        self.assertTrue(self.config._open_config())
        self.assertTrue(self.config.config)

    def test_load_config(self):
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"key": "value"}'
            self.assertTrue(self.config.load_config())
            self.assertEqual(self.config.config, {"key": "value"})

    def test_load_config_empty_file(self):
        config = Config("tests/test_files/empty_file.json")
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = ''
            self.assertFalse(config.load_config())
            self.assertIsNone(config.config)

    def test_load_config_file_not_found(self):
        config = Config("tests/test_files/nonexistent_file.json")
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = FileNotFoundError
            self.assertFalse(config.load_config())
            self.assertIsNone(config.config)
