import os
import unittest

from cmdtools.castorclient2.castorclient2 import CastorClient

with open('{}/castorclientid.txt'.format(os.environ['HOME']), 'r') as f:
    CLIENT_ID = f.readline().strip()
with open('{}/castorclientsecret.txt'.format(os.environ['HOME']), 'r') as f:
    CLIENT_SECRET = f.readline().strip()


STUDY_DPCA = 'ESPRESSO_v2.0_DPCA'
STUDY_DHBA = 'ESPRESSO_v2.0_DHBA'


class TestCastorClient(unittest.TestCase):

    def test_client(self):

        # Connect to Castor EDC and verify that session is valid
        self.client = CastorClient()
        self.client.connect(CLIENT_ID, CLIENT_SECRET)
        self.assertIsNotNone(self.client._session)

        # Verify that selected study is None
        self.assertIsNone(self.client._selected_study)

        # Select DPCA study
        self.client.select_study(STUDY_DPCA)
        self.assertIsNotNone(self.client._selected_study)
        self.assertEqual(self.client._selected_study['name'], STUDY_DPCA)

        # Select DHBA study
        self.client.select_study(STUDY_DHBA)
        self.assertIsNotNone(self.client._selected_study)
        self.assertEqual(self.client._selected_study['name'], STUDY_DHBA)


if __name__ == '__main__':
    unittest.main()
