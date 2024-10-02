import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from api import parser

class TestParser(unittest.TestCase):

    @patch("api.parser.openpyxl.load_workbook")
    def test_load_sheet(self, mock_load_workbook):
        mock_workbook = MagicMock()
        mock_workbook.sheetnames = ["Sheet1", "Sheet2", "Sheet3", "Sheet4"]
        mock_workbook.__getitem__.return_value = "MockSheet"
        
        mock_load_workbook.return_value = mock_workbook
        
        result = parser.load_sheet("test_path.xlsx")
        self.assertEqual(result, "MockSheet")
        mock_load_workbook.assert_called_once_with(filename="test_path.xlsx", data_only=True, read_only=True)

    def test_ingest_specs(self):
        mock_sheet = MagicMock()
        mock_sheet.iter_rows.return_value = [
            [None, MagicMock(value="Drainage"), MagicMock(value="Value1")],
            [None, MagicMock(value="Shearing"), MagicMock(value="Value2")],
        ]
        
        result = parser.ingest_specs(mock_sheet)
        
        expected_output = {"drainage": "value1", "shearing": "value2"}
        self.assertEqual(result, expected_output)

    def test_ingest_table(self):
        # Create a sample DataFrame that represents what the actual sheet might look like
        data = [
            ["Stage no.", "Axial Strain", "Volumetric Strain", "Excess PWP"],
            [1, 0.02, 0.03, 120],
            [2, 0.05, 0.08, 130],
            [3, 0.10, 0.15, 140],
            [None, None, None, None]  # Represents the end of the table
        ]

        mock_df = pd.DataFrame(data)
        result = parser.ingest_table(mock_df)

        print(result)  # Print to view
        return result  # Return result

    @patch("api.parser.load_sheet")
    @patch("api.parser.ingest_specs")
    @patch("api.parser.ingest_table")
    def test_parse_workbook(self, mock_ingest_table, mock_ingest_specs, mock_load_sheet):
        mock_load_sheet.return_value = "MockSheet"
        mock_ingest_specs.return_value = {"drainage": "value1"}
        mock_ingest_table.return_value = pd.DataFrame({
            "axial strain": [1, 2, 3],
            "volumetric strain": [4, 5, 6],
        })
        
        specs, df = parser.parse_workbook("test_path.xlsx")
        self.assertEqual(specs, {"drainage": "value1"})
        self.assertEqual(df.shape, (3, 2))
        
        mock_load_sheet.assert_called_once_with("test_path.xlsx")
        mock_ingest_specs.assert_called_once_with("MockSheet")
        mock_ingest_table.assert_called_once_with("MockSheet")
        return specs, df  # Return results

if __name__ == "__main__":
    unittest.main()
