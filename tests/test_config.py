import unittest
from config.config import Config


class TestConfit(unittest.TestCase):
    def test_open_file(self):
        test_cfg_1 = Config("", False)
        self.assertFalse(test_cfg_1._open_config())
        self.assertIsNone(test_cfg_1.config)

        test_cfg_2 = Config("tests/test_files/test_config_2.json", False)
        self.assertFalse(test_cfg_2._open_config())
        self.assertIsNone(test_cfg_2.config)

        test_cfg_3 = Config("tests/test_files/test_config.json", False)
        self.assertTrue(test_cfg_3._open_config())
        self.assertIsNotNone(test_cfg_3.config)

    def test_env(self):
        test_cfg_1 = Config("", True)
        test_cfg_1.set_env_path("")
        test_cfg_1._load_env()
        self.assertFalse(test_cfg_1.env)
        self.assertIsNone(test_cfg_1.get_username())
        self.assertIsNone(test_cfg_1.get_password())
        self.assertFalse(test_cfg_1.is_institutional())

        test_cfg_2 = Config("", True)
        test_cfg_2.set_env_path("tests\\test_files\\test.env")
        self.assertEqual(test_cfg_2._env_path, "tests\\test_files\\test.env")
        self.assertTrue(test_cfg_2._use_env)
        self.assertFalse(test_cfg_2.env)
        self.assertIsNone(test_cfg_2.get_username())
        self.assertIsNone(test_cfg_2.get_password())
        self.assertFalse(test_cfg_2.is_institutional())

        test_cfg_2._load_env()
        self.assertTrue(test_cfg_2.env)
        self.assertEqual(test_cfg_2.get_username(), "test_username")
        self.assertEqual(test_cfg_2.get_password(), "test_password")
        self.assertTrue(test_cfg_2.is_institutional())

    def test_load(self):
        test_cfg_1 = Config("tests/test_files/test_config.json", False)
        self.assertTrue(test_cfg_1.load_config())
        self.assertIsNotNone(test_cfg_1.config)

        test_cfg_2 = Config("tests/test_files/test_config.json", True)
        test_cfg_2.set_env_path("tests\\test_files\\test.env")
        self.assertTrue(test_cfg_2.load_config())
        self.assertIsNotNone(test_cfg_2.config)
        self.assertTrue(test_cfg_2.env)
        self.assertEqual(test_cfg_2.get_username(), "test_username")
        self.assertEqual(test_cfg_2.get_password(), "test_password")
        self.assertTrue(test_cfg_2.is_institutional())
