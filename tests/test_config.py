import unittest
from unittest.mock import patch
from src.config.config import Config


class TestConfig(unittest.TestCase):
    def test_open_config(self):
        config = Config()
        self.assertTrue(config._open_config())
        self.assertTrue(config.config)

    def test_load_config(self):
        config = Config()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"key": "value"}'
            self.assertTrue(config.load_config())
            self.assertEqual(config.config, {"key": "value"})

    def test_load_config_empty_file(self):
        config = Config()
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = ''
            self.assertFalse(config.load_config())
            self.assertIsNone(config.config)

    def test_load_config_file_not_found(self):
        config = Config()
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = FileNotFoundError
            self.assertFalse(config.load_config())
            self.assertIsNone(config.config)
