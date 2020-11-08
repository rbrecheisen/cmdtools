from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from cmdtools.castorclient.process import *

BASE_URL = 'https://data.castoredc.com'
TOKEN_URL = BASE_URL + '/oauth/token'
API_URL = BASE_URL + '/api'


class CastorImportAndUpdateClient(object):

    def __init__(self):
        self._session = None
        self._studies = None
        self._selected_study = None

    def connect(self, client_id, client_secret):
        self._session = self._create_session(client_id, client_secret)
        self._studies = self._get_studies(self._session)
        self._selected_study = None

    def select_study(self, study_name):
        for study in self._studies:
            if study['name'] == study_name:
                self._selected_study = study
                break
        print('Selected study {}'.format(self._selected_study['name']))

    @staticmethod
    def _create_session(client_id, client_secret):
        print('Connecting to Castor EDC...')
        client = BackendApplicationClient(client_id=client_id)
        client_session = OAuth2Session(client=client)
        client_session.fetch_token(
            token_url=TOKEN_URL,
            client_id=client_id,
            client_secret=client_secret,
        )
        return client_session

    @staticmethod
    def _get_studies(session):
        print('Getting studies...')
        response = session.get(API_URL + '/study').json()
        studies = []
        idx = 1
        for study in response['_embedded']['study']:
            studies.append(study)
            idx += 1
        return studies

    @staticmethod
    def import_dica_data(
        dica_excel_file,            # DICA file (in Excel format)
        columns_int_to_string,      # Names of columns to be converted from int to str
        mapping_excel_file,         # Excel file containing mapping from DICA variable names to Castor field names
        mapping_key_column,         # Name of column to serve as key in mapping
        mapping_value_column,       # Name of column to serve as value in mapping
    ):
        df = pd.read_excel(dica_excel_file)
        processing_steps = [
            ConvertColumnsFromIntToString(column_names=columns_int_to_string),
            ChangeColumnDatesToFormattedString(date_format='%d-%m-%Y'),
            MapDicaToCastorColumnNames(
                mapping_excel_file=mapping_excel_file,
                key_column=mapping_key_column, value_column=mapping_value_column)
        ]
        for processing_step in processing_steps:
            df = processing_step.execute(df)
