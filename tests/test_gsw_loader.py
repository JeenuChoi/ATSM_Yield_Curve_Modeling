import unittest
import pandas as pd
import numpy as np
import os
from src.data.gsw_loader import load_gsw_data

class TestGswLoader(unittest.TestCase):
    def setUp(self):
        # Create a dummy CSV file that mimics the structure of feds200628.csv
        self.test_dir = 'Desktop/ATSM_Project/tests'
        self.dummy_csv_path = os.path.join(self.test_dir, 'dummy_feds200628.csv')
        self.create_dummy_csv()

    def tearDown(self):
        # Clean up the dummy CSV file after tests
        if os.path.exists(self.dummy_csv_path):
            os.remove(self.dummy_csv_path)

    def create_dummy_csv(self):
        header = "Note: This is not an official Federal Reserve statistical release.\n" * 5
        columns = "Date,BETA0,SVENY01,SVENY02,SVENY03,SVENY05,SVENY07,SVENY10,SVENY20,SVENY30,OTHER\n"
        data_rows = [
            "1990-01-15,1,5.0,5.1,5.2,5.4,5.6,5.9,6.5,7.0,X",
            "1990-01-31,2,5.01,5.11,5.21,5.41,5.61,5.91,6.51,7.01,Y", # EOM
            "1990-02-15,3,5.02,5.12,5.22,5.42,5.62,5.92,6.52,7.02,Z",
            "1990-02-28,4,5.03,5.13,5.23,5.43,5.63,5.93,6.53,7.03,W", # EOM
            "1990-03-15,5,5.04,5.14,NA,5.44,5.64,5.94,6.54,7.04,V", # Row with NA, but not last of month
            "1990-03-31,6,5.05,5.15,5.25,5.45,5.65,5.95,6.55,7.05,U"  # EOM
        ]
        
        content = header + columns + "\n".join(data_rows)
        
        os.makedirs(self.test_dir, exist_ok=True)
        with open(self.dummy_csv_path, 'w') as f:
            f.write(content)

    def test_load_gsw_data(self):
        df = load_gsw_data(self.dummy_csv_path)
        
        # 1. Test DataFrame shape
        # Should have 3 rows (Jan, Feb, Mar EOM) as the NA value was not on a month-end row that was selected.
        self.assertEqual(df.shape, (3, 8))

        # 2. Test index
        self.assertIsInstance(df.index, pd.DatetimeIndex)
        expected_index = pd.to_datetime(['1990-01-31', '1990-02-28', '1990-03-31']).rename('Date')
        expected_index.freq = 'ME'
        self.assertTrue(df.index.equals(expected_index))

        # 3. Test columns
        expected_columns = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
        self.assertListEqual(df.columns.tolist(), expected_columns)

        # 4. Test values
        # Check Jan 31 data (converted from % to decimal)
        jan_yields = df.loc['1990-01-31']
        self.assertAlmostEqual(jan_yields[1.0], 0.0501)
        self.assertAlmostEqual(jan_yields[2.0], 0.0511)
        self.assertAlmostEqual(jan_yields[3.0], 0.0521)

        # Check Feb 28 data
        feb_yields = df.loc['1990-02-28']
        self.assertAlmostEqual(feb_yields[10.0], 0.0593)
        self.assertAlmostEqual(feb_yields[30.0], 0.0703)
        
        # Check Mar 31 data
        mar_yields = df.loc['1990-03-31']
        self.assertAlmostEqual(mar_yields[1.0], 0.0505)


    def test_load_nonexistent_file(self):
        # Test that it handles a non-existent file gracefully
        df = load_gsw_data("nonexistent_file.csv")
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)