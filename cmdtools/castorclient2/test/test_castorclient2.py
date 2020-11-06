import os
import unittest

from cmdtools.castorclient2.castorclient2 import CastorClient

with open('{}/castorclientid.txt'.format(os.environ['HOME']), 'r') as f:
    CLIENT_ID = f.readline().strip()
with open('{}/castorclientsecret.txt'.format(os.environ['HOME']), 'r') as f:
    CLIENT_SECRET = f.readline().strip()


DPCA_STUDY = 'ESPRESSO_v2.0_DPCA'
DHBA_STUDY = 'ESPRESSO_v2.0_DHBA'
DHBA_EXCEL_FILE_PATH = '/Users/ralph/Desktop/Export_DHBA_academisch-ziekenhuis-maastricht_01042020.xlsx'


class TestCastorClient(unittest.TestCase):

    def test_client(self):

        self.client = CastorClient()

        # # Connect to Castor EDC and verify that session is valid
        # self.client.connect(CLIENT_ID, CLIENT_SECRET)
        # self.assertIsNotNone(self.client._session)
        #
        # # Verify that selected study is None
        # self.assertIsNone(self.client._selected_study)
        #
        # # Select DPCA study
        # self.client.select_study(DPCA_STUDY)
        # self.assertIsNotNone(self.client._selected_study)
        # self.assertEqual(self.client._selected_study['name'], DPCA_STUDY)
        #
        # # Select DHBA study
        # self.client.select_study(DHBA_STUDY)
        # self.assertIsNotNone(self.client._selected_study)
        # self.assertEqual(self.client._selected_study['name'], DHBA_STUDY)

        # Import DICA data
        self.client.import_dica_data(DHBA_EXCEL_FILE_PATH)


if __name__ == '__main__':
    unittest.main()
