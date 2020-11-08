import os

from cmdtools.castorclient import CastorClient, CastorCloudInstance


# TODO: Move these globals to a separate file
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


def test_drive_upload_dhba_data_to_castor_cloud_instance():
    """
    Tests whether the test drive of uploading DHBA data to Castor EDC works as expected, i.e., there is
    no actual data uploaded but a report is created that specifies exactly which new records will be
    created, as well as which records will be skipped (because they already exist in Castor).
    """

    # Create Castor client
    client = CastorClient()

    # Import DHBA data into client
    data = client.import_dhba_data(DHBA_EXCEL_FILE_PATH)

    # Connect to Castor EDC cloud
    cloud_instance = CastorCloudInstance()

    # Test drive the upload of DHBA data to Castor EDC cloud
    client.test_drive_upload_to_cloud_instance(data, cloud_instance)

    # Get test report for the upload test drive
    test_report = client.get_upload_test_report()

    # Verify the test report indicates a successful test drive
    assert test_report.is_test_upload_successful()
