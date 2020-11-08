import os
import unittest

from cmdtools.castorclient import CastorClient

HOME = os.environ['HOME']

with open('{}/castorclientid.txt'.format(HOME), 'r') as f:
    CLIENT_ID = f.readline().strip()
with open('{}/castorclientsecret.txt'.format(HOME), 'r') as f:
    CLIENT_SECRET = f.readline().strip()

DPCA_STUDY = 'ESPRESSO_v2.0_DPCA'
DHBA_STUDY = 'ESPRESSO_v2.0_DHBA'
DHBA_EXCEL_FILE_PATH = '{}/Desktop/Export_DHBA_academisch-ziekenhuis-maastricht_01042020.xlsx'.format(HOME)
DHBA_COLUMNS_INT_TO_STRING = ['upn', 'verrichting-upn']
DHBA_MAPPING_FILE_PATH = '{}/Desktop/DHBA_var_mapping_to_Castor.xlsx'.format(HOME)
DHBA_KEY_COLUMN = 'dica'
DHBA_VALUE_COLUMN = 'castor'


class TestCastorClient(unittest.TestCase):

    def test_import_and_update(self):

        self.client = CastorClient()

        # Connect to Castor EDC and verify that session is valid
        self.client.connect(CLIENT_ID, CLIENT_SECRET)
        self.assertIsNotNone(self.client._session)

        # Verify that selected study is None
        self.assertIsNone(self.client._selected_study)

        # Select DPCA study
        self.client.select_study(DPCA_STUDY)
        self.assertIsNotNone(self.client._selected_study)
        self.assertEqual(self.client._selected_study['name'], DPCA_STUDY)

        # Select DHBA study
        self.client.select_study(DHBA_STUDY)
        self.assertIsNotNone(self.client._selected_study)
        self.assertEqual(self.client._selected_study['name'], DHBA_STUDY)

        # Import DICA data
        self.client.import_dica_data(
            DHBA_EXCEL_FILE_PATH,
            DHBA_COLUMNS_INT_TO_STRING,
            DHBA_MAPPING_FILE_PATH,
            DHBA_KEY_COLUMN, DHBA_VALUE_COLUMN,
        )

        # Check that import went ok
        # ???


if __name__ == '__main__':
    unittest.main()
