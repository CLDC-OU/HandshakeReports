
from enum import Enum
import unittest
from dataset.dataset import DataSet, Column
import pandas as pd


class TestDataSet(unittest.TestCase):
    @staticmethod
    def get_test_cols() -> dict[str, str]:
        """Generate basic test columns for a DataSet

        Returns:
            dict: the columns dictionary including the id and date columns
        """
        return {"id": "test_col", "date": "date_col"}

    @staticmethod
    def get_test_1():
        """Generate the test input for a DataSet with an empty DataFrame and 2 defined columns

        Returns:
            tuple: the test id, test DataFrame, and test columns
                test_id: str
                test_df: pd.DataFrame
                test_cols: dict[str, str]
        """

        test_1_id = "test_1_id"
        test_1_df = pd.DataFrame()
        test_1_cols = TestDataSet.get_test_cols()
        return test_1_id, test_1_df, test_1_cols

    @staticmethod
    def get_test_2():
        """Generate the test input for a DataSet with a valid DataFrame with 2 rows and 2 defined columns

        Returns:
            tuple: the test id, test DataFrame, and test columns
                test_id: str
                test_df: pd.DataFrame
                test_cols: dict[str, str]
        """
        test_2_id = "test_2_id"
        test_2_df = pd.DataFrame({
            "test_col": ["test_val_1", "test_val_2"],
            "test_date_col": ["2023-01-02", "2023-01-01"]
        })
        test_2_cols = {"id": "test_col", "date": "invalid_date_col"}
        return test_2_id, test_2_df, test_2_cols

    def test_init(self):
        with self.assertRaises(ValueError) as context:
            DataSet(None, None, None)  # type: ignore
        self.assertIn("df must be a valid DataFrame", str(context.exception))

        with self.assertRaises(ValueError) as context:
            DataSet(None, pd.DataFrame(), None)  # type: ignore
        self.assertIn("cols must be a valid dictionary", str(context.exception))

        test_1_id = "test_1_id"
        test_1_df = pd.DataFrame({
            "test_col": ["test_val_1", "test_val_2", "test_val_3", "test_val_4", "test_val_5", "test_val_6", "test_val_7", "test_val_8"],
            "test_date_col": ["2023-01-03", "2023-01-01", "2023-01-02", "2022-01-01", "2022-02-01", "2022-03-01", "2023-02-01", "2023-03-01"]
        })
        test_1_cols = TestDataSet.get_test_cols()

        test_1_dataset = DataSet(test_1_id, test_1_df, test_1_cols)
        self.assertEqual(test_1_dataset.id, "test_1_id")
        self.assertIsNotNone(test_1_dataset.df)
        self.assertEqual(test_1_dataset.cols, test_1_cols)
        self.assertIs(test_1_dataset.df, test_1_df)

    def test_get_col_name(self):
        test_id = "test_id"
        test_cols = TestDataSet.get_test_cols()
        test_df = pd.DataFrame()

        # ==================== TEST 1 ===================== #
        #                                                   #
        #            Defined Columns in DataSet             #
        #                                                   #
        # ================================================= #
        test_1_dataset = DataSet(*TestDataSet.get_test_1())
        self.assertEqual(test_1_dataset.get_col_name(Column.ID), "test_col")
        self.assertEqual(test_1_dataset.get_col_name(Column.DATE), "date_col")

        # ==================== TEST 2 ===================== #
        #                                                   #
        #              Columns Not in DataSet               #
        #                                                   #
        # ================================================= #
        test_cols = {"test": "test"}
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        self.assertIsNone(test_2_dataset.get_col_name(Column.ID))
        self.assertIsNone(test_2_dataset.get_col_name(Column.DATE))

        # ==================== TEST 3 ===================== #
        #                                                   #
        #              Invalid Column Names                 #
        #                                                   #
        # ================================================= #
        test_cols = {"_id": "invalid_id", "INVALID_COL": "invalid_col"}
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        self.assertTrue(test_3_dataset.get_col_name(Column.ID) != "invalid_id")

        class InvalidColumn(Enum):
            ID = "id"
        with self.assertRaises(ValueError) as context:
            test_3_dataset.get_col_name(InvalidColumn.ID)
        self.assertIn("col_id must be a Column Enum", str(context.exception))

        with self.assertRaises(ValueError) as context:
            test_3_dataset.get_col_name(None)  # type: ignore
        self.assertIn("col_id must be a Column Enum", str(context.exception))

        # ==================== TEST 3 ===================== #
        #                                                   #
        #             Overloaded Column Names               #
        #                                                   #
        # ================================================= #
        self.assertIsNone(test_3_dataset.get_col_name(Column.APPOINTMENT_TYPE))

    def test_get_col(self):
        test_id = "test_id"
        test_cols = TestDataSet.get_test_cols()
        test_df = None

        # ==================== TEST 1 ===================== #
        #                                                   #
        #                   Invalid Column                  #
        #                                                   #
        # ================================================= #
        test_cols = {"test": "test"}
        test_df = pd.DataFrame({"test": ["test_val_1", "test_val_2"]})
        test_1_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_1_dataset.get_col("invalid_col")  # type: ignore
        self.assertIn("col_id must be a Column Enum", str(context.exception))

        # ==================== TEST 2 ===================== #
        #                                                   #
        #                  Unknown Columns                  #
        #                                                   #
        # ================================================= #
        test_cols = {"test": "test"}
        test_df = pd.DataFrame({"test": ["test_val_1", "test_val_2"]})
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_2_dataset.get_col(Column.ID)
        self.assertIn("col_id must be a defined column", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_2_dataset.get_col(Column.DATE)
        self.assertIn("col_id must be a defined column", str(context.exception))

        # ==================== TEST 3 ===================== #
        #                                                   #
        #          Columns Not Defined in DataFrame         #
        #                                                   #
        # ================================================= #
        test_cols = {"id": "test_col", "date": "test_date_col"}
        test_df = pd.DataFrame({"test": ["test_val_1", "test_val_2"]})
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_3_dataset.get_col(Column.ID)
        self.assertIn("col_id must be in DataFrame", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_3_dataset.get_col(Column.DATE)
        self.assertIn("col_id must be in DataFrame", str(context.exception))

        # ==================== TEST 4 ===================== #
        #                                                   #
        #           Columns Defined in DataFrame            #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_col": ["test_val_1", "test_val_2"],
            "test_date_col": ["2023-01-02", "2023-01-01"]
        })
        test_cols = {"id": "test_col", "date": "test_date_col"}
        test_4_dataset = DataSet(test_id, test_df, test_cols)
        self.assertTrue(test_4_dataset.get_col(Column.ID).equals(pd.Series(["test_val_1", "test_val_2"])))
        self.assertTrue(test_4_dataset.get_col(Column.DATE).equals(pd.Series(["2023-01-02", "2023-01-01"])))

    def test_sort_date(self):
        test_id = "test_id"
        test_cols = TestDataSet.get_test_cols()
        test_df = None

        # ==================== TEST 1 ===================== #
        #                                                   #
        #           Date Column Not in DataFrame            #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]})
        test_cols = {"id": "test_col", "date": "invalid_date_col"}
        test_1_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_1_dataset.sort_date()
        self.assertIn("DataFrame must have a date column", str(context.exception))

        # ==================== TEST 2 ===================== #
        #                                                   #
        #                Unsorted DataFrame                 #
        #                      by day                       #
        #                    length = 2                     #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_col": ["test_val_1", "test_val_2"],
            "test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]
        })
        expected_output = pd.DataFrame({
            "test_col": ["test_val_2", "test_val_1"],
            "test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-01-02")]
        })
        test_cols = {"id": "test_col", "date": "test_date_col"}
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        test_2_dataset.sort_date()
        test_2_dataset.reset_index()
        self.assertTrue(test_2_dataset.get_df().equals(expected_output))

        del test_df

        # ==================== TEST 3 ===================== #
        #                                                   #
        #                 Sorted DataFrame                  #
        #                    length = 2                     #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_col": ["test_val_1", "test_val_2"],
            "test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-01-02")]
        })
        expected_output = test_df
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        test_3_dataset.sort_date()
        self.assertTrue(test_3_dataset.get_df().equals(expected_output))
        self.assertIs(test_3_dataset.get_df(), expected_output)

        del test_df

        # ==================== TEST 4 ===================== #
        #                                                   #
        #                 Unsorted DataFrame                #
        #                  by month and year                #
        #                     length = 4                    #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_col": [
                "test_val_1",
                "test_val_2",
                "test_val_3",
                "test_val_4"
            ],
            "test_date_col": [
                pd.to_datetime("2022-02-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2021-11-30")
            ]
        })
        expected_output = pd.DataFrame({
            "test_col": [
                "test_val_4",
                "test_val_1",
                "test_val_3",
                "test_val_2"
            ],
            "test_date_col": [
                pd.to_datetime("2021-11-30"),
                pd.to_datetime("2022-02-01"),
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-04-01")
            ]
        })
        test_4_dataset = DataSet(test_id, test_df, test_cols)
        test_4_dataset.sort_date()
        test_4_dataset.reset_index()
        self.assertTrue(test_4_dataset.get_df().equals(expected_output))

    def test_filter_months(self):
        test_id = "test_id"
        test_cols = TestDataSet.get_test_cols()
        test_df = None

        # ==================== TEST 1 ===================== #
        #                                                   #
        #                Invalid Month Input                #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]})
        test_cols = {"date": "test_date_col"}
        test_1_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_months("invalid_month_input")
        self.assertIn("Invalid month input", str(context.exception))

        # ==================== TEST 2 ===================== #
        #                                                   #
        #              Filter By Single Month               #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]})
        expected_output = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]})
        test_cols = {"date": "test_date_col"}
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        test_2_dataset.filter_months("January")
        test_2_dataset.reset_index()
        self.assertTrue(test_2_dataset.get_df().equals(expected_output))

        del test_2_dataset

        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-02-01")]})
        expected_output = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01")]})
        test_cols = {"date": "test_date_col"}
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        test_2_dataset.filter_months("January")
        test_2_dataset.reset_index()
        self.assertTrue(test_2_dataset.get_df().equals(expected_output))

        # ==================== TEST 3 ===================== #
        #                                                   #
        #             Filter By Multiple Months             #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01"), pd.to_datetime("2023-04-01")]})
        expected_output = test_df
        test_cols = {"date": "test_date_col"}
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        test_3_dataset.filter_months("January", "April")
        self.assertTrue(test_3_dataset.get_df().equals(expected_output))
        self.assertIs(test_3_dataset.get_df(), expected_output)

        del test_3_dataset

        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-02-01"), pd.to_datetime("2023-04-01"), pd.to_datetime("2023-05-01")]})
        expected_output = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-04-01")]})
        test_cols = {"date": "test_date_col"}
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        test_3_dataset.filter_months("January", "April")
        test_3_dataset.reset_index()
        self.assertTrue(test_3_dataset.get_df().equals(expected_output))

        # ==================== TEST 4 ===================== #
        #                                                   #
        #               Filter By Month Range               #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01"), pd.to_datetime("2023-04-01")]})
        expected_output = test_df
        test_cols = {"date": "test_date_col"}
        test_4_dataset = DataSet(test_id, test_df, test_cols)
        test_4_dataset.filter_months("January-April")
        self.assertTrue(test_4_dataset.get_df().equals(expected_output))
        self.assertIs(test_4_dataset.get_df(), expected_output)

        del test_4_dataset

        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-02-01"), pd.to_datetime("2023-04-01"), pd.to_datetime("2023-05-01")]})
        expected_output = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-01"), pd.to_datetime("2023-02-01")]})
        test_cols = {"date": "test_date_col"}
        test_4_dataset = DataSet(test_id, test_df, test_cols)
        test_4_dataset.filter_months("January-February")
        test_4_dataset.reset_index()
        self.assertTrue(test_4_dataset.get_df().equals(expected_output))

        # ==================== TEST 5 ===================== #
        #                                                   #
        #          Filter By Multiple Month Ranges          #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-02"),
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-10-01"),
                pd.to_datetime("2023-11-01"),
                pd.to_datetime("2023-12-01")
            ]}
        )
        expected_output = test_df
        test_cols = {"date": "test_date_col"}
        test_5_dataset = DataSet(test_id, test_df, test_cols)
        test_5_dataset.filter_months("January-April", "October-December")
        self.assertTrue(test_5_dataset.get_df().equals(expected_output))
        self.assertIs(test_5_dataset.get_df(), expected_output)

        del test_5_dataset

        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-03-01"),
                pd.to_datetime("2023-06-01"),
                pd.to_datetime("2023-09-01"),
                pd.to_datetime("2023-11-01")
            ]}
        )
        expected_output = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-11-01")
            ]}
        )
        test_cols = {"date": "test_date_col"}
        test_5_dataset = DataSet(test_id, test_df, test_cols)
        test_5_dataset.filter_months("January-February", "October-December")
        test_5_dataset.reset_index()
        self.assertTrue(test_5_dataset.get_df().equals(expected_output))

        # ==================== TEST 6 ===================== #
        #                                                   #
        #                    Filter By                      #
        #                   Month Range                     #
        #                       and                         #
        #                   Single Month                    #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-02"),
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-12-01")
            ]}
        )
        expected_output = test_df
        test_cols = {"date": "test_date_col"}
        test_6_dataset = DataSet(test_id, test_df, test_cols)
        test_6_dataset.filter_months("January-April", "December")
        self.assertTrue(test_6_dataset.get_df().equals(expected_output))
        self.assertIs(test_6_dataset.get_df(), expected_output)

        del test_6_dataset

        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-03-01"),
                pd.to_datetime("2023-06-01"),
                pd.to_datetime("2023-09-01"),
                pd.to_datetime("2023-11-01")
            ]}
        )
        expected_output = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-11-01")
            ]}
        )
        test_cols = {"date": "test_date_col"}
        test_6_dataset = DataSet(test_id, test_df, test_cols)
        test_6_dataset.filter_months("January-February", "November")
        test_6_dataset.reset_index()
        self.assertTrue(test_6_dataset.get_df().equals(expected_output))

        # ==================== TEST 7 ===================== #
        #                                                   #
        #                Filter By Multiple                 #
        #                   Month Ranges                    #
        #                        and                        #
        #                   Single Months                   #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-08-01"),
                pd.to_datetime("2023-10-01"),
                pd.to_datetime("2023-11-01"),
                pd.to_datetime("2023-12-01")
            ]}
        )
        expected_output = test_df
        test_cols = {"date": "test_date_col"}
        test_7_dataset = DataSet(test_id, test_df, test_cols)
        test_7_dataset.filter_months("January-February", "April", "August", "October-December")
        self.assertTrue(test_7_dataset.get_df().equals(expected_output))
        self.assertIs(test_7_dataset.get_df(), expected_output)

        del test_7_dataset

        test_df = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-07-01"),
                pd.to_datetime("2023-09-01"),
                pd.to_datetime("2023-12-01")
            ]}
        )
        expected_output = pd.DataFrame(
            {"test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2023-02-01"),
                pd.to_datetime("2023-04-01"),
                pd.to_datetime("2023-12-01")
            ]}
        )
        test_cols = {"date": "test_date_col"}
        test_7_dataset = DataSet(test_id, test_df, test_cols)
        test_7_dataset.filter_months("January-February", "April", "August", "October-December")
        test_7_dataset.reset_index()
        self.assertTrue(test_7_dataset.get_df().equals(expected_output))

    def test_filter_years(self):
        test_id = "test_id"
        test_cols = TestDataSet.get_test_cols()
        test_df = None

        # ==================== TEST 1 ===================== #
        #                                                   #
        #                Invalid Year Input                #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({"test_date_col": [pd.to_datetime("2023-01-02"), pd.to_datetime("2023-01-01")]})
        test_cols = {"date": "test_date_col"}
        test_1_dataset = DataSet(test_id, test_df, test_cols)
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_years("error")
        self.assertIn("Invalid year range", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_years("2023-2022")
        self.assertIn("Invalid year range", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_years("2023-error")
        self.assertIn("Invalid year range", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_years("error-2023")
        self.assertIn("Invalid year range", str(context.exception))
        with self.assertRaises(ValueError) as context:
            test_1_dataset.filter_years("")
        self.assertIn("Invalid year range", str(context.exception))

        # ==================== TEST 2 ===================== #
        #                                                   #
        #              Filter By Single Year               #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_2_dataset = DataSet(test_id, test_df, test_cols)
        test_2_dataset.filter_years("2023")
        test_2_dataset.reset_index()
        self.assertTrue(test_2_dataset.get_df().equals(expected_output))

        # ==================== TEST 3 ===================== #
        #                                                   #
        #              Filter By Multiple Years             #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2021-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_3_dataset = DataSet(test_id, test_df, test_cols)
        test_3_dataset.filter_years("2023", "2022")
        test_3_dataset.reset_index()
        self.assertTrue(test_3_dataset.get_df().equals(expected_output))

        # ==================== TEST 4 ===================== #
        #                                                   #
        #               Filter By Year Range                #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2021-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_4_dataset = DataSet(test_id, test_df, test_cols)
        test_4_dataset.filter_years("2022-2023")
        test_4_dataset.reset_index()
        self.assertTrue(test_4_dataset.get_df().equals(expected_output))

        # ==================== TEST 5 ===================== #
        #                                                   #
        #          Filter By Multiple Year Ranges           #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2021-01-01"),
                pd.to_datetime("2020-01-01"),
                pd.to_datetime("2019-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2020-01-01"),
                pd.to_datetime("2019-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_5_dataset = DataSet(test_id, test_df, test_cols)
        test_5_dataset.filter_years("2022-2023", "2019-2020")
        test_5_dataset.reset_index()
        self.assertTrue(test_5_dataset.get_df().equals(expected_output))

        # ==================== TEST 6 ===================== #
        #                                                   #
        #                    Filter By                      #
        #                   Year Range                      #
        #                       and                         #
        #                   Single Year                     #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2021-01-01"),
                pd.to_datetime("2020-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2020-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_6_dataset = DataSet(test_id, test_df, test_cols)
        test_6_dataset.filter_years("2022-2023", "2020")
        test_6_dataset.reset_index()
        self.assertTrue(test_6_dataset.get_df().equals(expected_output))

        # ==================== TEST 7 ===================== #
        #                                                   #
        #                Filter By Multiple                 #
        #                   Year Ranges                     #
        #                        and                        #
        #                   Single Years                    #
        #                                                   #
        # ================================================= #
        test_df = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2021-01-01"),
                pd.to_datetime("2020-01-01"),
                pd.to_datetime("2018-01-01")
            ]
        })
        expected_output = pd.DataFrame({
            "test_date_col": [
                pd.to_datetime("2023-01-01"),
                pd.to_datetime("2022-01-01"),
                pd.to_datetime("2020-01-01"),
                pd.to_datetime("2018-01-01")
            ]
        })
        test_cols = {"date": "test_date_col"}
        test_7_dataset = DataSet(test_id, test_df, test_cols)
        test_7_dataset.filter_years("2022 - 2023", "2018", "2019-2020")
        test_7_dataset.reset_index()
        self.assertTrue(test_7_dataset.get_df().equals(expected_output))


if __name__ == "__main__":
    unittest.main()
