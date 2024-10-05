import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from api.datahandler import (
    commit_new_entry, retrieve_entry_data, retrieve_test_specs, change_path, get_path
)

class TestDataHandler(unittest.TestCase):

    @patch("api.datahandler.create_engine")
    @patch("api.datahandler.Session")
    def test_commit_new_entry(self, mock_session, mock_engine):
        # Prepare sample data
        mock_df = pd.DataFrame({
            'time start of stage': [0.1, 0.2],
            'axial strain': [0.01, 0.02],
            'volumetric strain': [0.003, 0.004],
            'excess pwp': [50, 60],
            'p\'': [100, 110],
            'deviator stress': [500, 600],
            'void ratio': [1.0, 0.95],
            'shear induced pwp': [20, 30],
        })

        specs = {
            'density': 'dense',
            'plasticity': 'plastic',
            'psd': 'sand',
            'availability': 'public',
            'drainage': 'drained',
            'shearing': 'compression',
            'consolidation': 1500,
            'anisotropy': 0.7
        }

        mock_session.return_value.__enter__.return_value.add = MagicMock()

        # Call the function
        commit_new_entry(specs, mock_df, 'test_file.xlsx')

        # Assertions
        mock_session.assert_called_once()  # Check if the session was created
        mock_session.return_value.__enter__.return_value.add.assert_called()  # Check if data was added to the session

    @patch("api.datahandler.create_engine")
    @patch("api.datahandler.Session")
    def test_retrieve_entry_data(self, mock_session, mock_engine):
        # Create a mock connection object for session.bind
        mock_connection = MagicMock()

        # Mock the session and data retrieval
        mock_session.return_value.__enter__.return_value.query.return_value.statement = "SELECT * FROM entry"
        mock_session.return_value.__enter__.return_value.bind = mock_connection  # Mock session.bind to use this connection

        # Mock the pandas read_sql function to return a DataFrame with 'test_id' column
        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame({
                'test_id': [1, 2],
                'time start of stage': [0.1, 0.2],
                'axial strain': [0.01, 0.02],
                'volumetric strain': [0.003, 0.004],
                'excess pwp': [50, 60],
                'p\'': [100, 110],
                'deviator stress': [500, 600],
                'void ratio': [1.0, 0.95],
                'shear induced pwp': [20, 30],
            })

            # Call the function
            result = retrieve_entry_data()

            # Assertions
            mock_session.assert_called_once()  # Ensure session is created
            self.assertIsInstance(result, pd.DataFrame)  # The result should be a DataFrame
            self.assertIn('test_id', result.columns)  # Ensure 'test_id' column is in the result

    @patch("api.datahandler.create_engine")
    @patch("api.datahandler.Session")
    def test_retrieve_test_specs(self, mock_session, mock_engine):
        # Create a mock connection object for session.bind
        mock_connection = MagicMock()

        # Mock the session and query
        mock_session.return_value.__enter__.return_value.query.return_value.statement = "SELECT * FROM test"
        mock_session.return_value.__enter__.return_value.bind = mock_connection  # Mock session.bind to use this connection

        # Mock the pandas read_sql function to return a DataFrame
        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame({
                'test_id': [1, 2],
                'availability_type': [True, False],
                'density_type': ['dense', 'loose'],
            })

            # Call the function
            result = retrieve_test_specs()

            # Assertions
            mock_session.assert_called_once()  # Ensure session is created
            self.assertIsInstance(result, pd.DataFrame)  # The result should be a DataFrame
            self.assertIn('test_id', result.columns)  # Ensure 'test_id' column is in the result

    def test_change_path(self):
        # Change path and check if it works correctly
        new_path = "/path/to/db.sqlite"
        change_path(new_path)
        self.assertIn("sqlite:////path/to/db.sqlite", get_path())  # Relaxed to check for the correct path

if __name__ == "__main__":
    unittest.main()
