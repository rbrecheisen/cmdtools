from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

"""
The purpose of the Castor Client class is to provide functionality for exploring, adding and updating data
in Castor EDC. Because exploration is a time-consuming process, requiring many iterations looping over records
and fields, we prefer to do exploration on the Castor export Excel file.
Adding and updating data must be done through the REST interface and requires connecting to the Castor EDC API
and directly manipulating the records and fields there.

The Castor Client class will be usable as a library in a Python script but can also be used via the command-line
using a wrapper shell script based on the cmd2 library.
"""

BASE_URL = 'https://data.castoredc.com'
TOKEN_URL = BASE_URL + '/oauth/token'
API_URL = BASE_URL + '/api'


class CastorExportClient(object):
    pass


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

class CastorClient(CastorExportClient, CastorImportAndUpdateClient):

    def __init__(self):
        super(CastorClient, self).__init__()