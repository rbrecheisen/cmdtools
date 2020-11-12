import os

from cmd2 import with_argument_list
from cmdtools.lib.shell import BasicShell
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

BASE_URL = 'https://data.castoredc.com'
TOKEN_URL = BASE_URL + '/oauth/token'
API_URL = BASE_URL + '/api'
INTRO = 'Welcome to the Castor REST Client!'
CLIENT_ID = open('{}/castorclientid.txt'.format(os.environ['HOME']), 'r').readline().strip()
CLIENT_SECRET = open('{}/castorclientsecret.txt'.format(os.environ['HOME']), 'r').readline().strip()


class CastorRESTClientShell(BasicShell):

    def __init__(self):
        super(CastorRESTClientShell, self).__init__()
        self.session = None
        self.studies = {}
        self.selected_study = None
        self.study_fields = {}
        self.study_records = {}
        self.study_record_data = {}
        self.debug = True
        self.intro = INTRO

    # HELPERS

    @staticmethod
    def create_session(client_id, client_secret):
        client = BackendApplicationClient(client_id=client_id)
        client_session = OAuth2Session(client=client)
        client_session.fetch_token(
            token_url=TOKEN_URL,
            client_id=client_id,
            client_secret=client_secret,
        )
        return client_session

    def get_fields(self):
        study_id = self.selected_study['study_id']
        url = API_URL + '/study/{}/field'.format(study_id)
        response = self.session.get(url).json()
        page_count = response['page_count']
        fields = {}
        for i in range(1, page_count + 1):
            url = API_URL + '/study/{}/field?page={}'.format(study_id, i)
            response = self.session.get(url).json()
            for field in response['_embedded']['fields']:
                fields[field['field_variable_name']] = field
        return fields

    def get_records(self):
        study_id = self.selected_study['study_id']
        url = API_URL + '/study/{}/record'.format(study_id)
        response = self.session.get(url).json()
        page_count = response['page_count']
        records = {}
        for i in range(1, page_count + 1):
            url = API_URL + '/study/{}/record?page={}'.format(study_id, i)
            response = self.session.get(url).json()
            for record in response['_embedded']['records']:
                if not record['id'].startswith('ARCHIVED'):
                    records[record['id']] = record
        return records

    def get_record_field_data(self, record_id, field):
        study_id = self.selected_study['study_id']
        url = API_URL + '/study/{}/record/{}/study-data-point/{}'.format(study_id, record_id, field['id'])
        response = self.session.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return None

    def get_record_data(self, record_id):
        record_data = {}
        for key in self.study_fields.keys():
            field = self.study_fields[key]
            field_data = self.get_record_field_data(record_id, field)
            if field_data is not None:
                self.poutput('{}: {}'.format(field['field_variable_name'], field_data['value']))
                record_data[field['field_variable_name']] = field_data
        return record_data

    def show_missing_record_data(self, record_id, verbose=True):
        missing_fields = []
        for key in self.study_fields.keys():
            field = self.study_fields[key]
            field_data = self.get_record_field_data(record_id, field)
            if field_data is None:
                if verbose:
                    self.poutput('{}'.format(field['field_variable_name']))
                else:
                    print('.', end='', flush=True)
                missing_fields.append(field['field_variable_name'])
        return missing_fields

    # CONNECT

    @with_argument_list()
    def do_connect(self, args):
        if len(args) != 2:
            self.poutput('Specify client ID and client secret separated by a space')
            return False
        self.poutput('Connecting to Castor EDC...')
        self.session = self.create_session(args[0], args[1])
        self.poutput('Ok')

    # STUDIES

    def do_show_studies(self, _):
        response = self.session.get(API_URL + '/study').json()
        idx = 1
        for study in response['_embedded']['study']:
            self.studies[idx] = study
            self.poutput('({}) {}'.format(idx, self.studies[idx]['name']))
            idx += 1
        self.poutput('Ok')

    def do_select_study(self, idx):
        self.selected_study = self.studies[int(idx)]
        self.poutput('Selected study: {}'.format(self.selected_study['name']))
        self.poutput('Loading fields definitions...')
        fields = self.get_fields()
        self.study_fields = fields
        self.poutput(len(self.study_fields))
        self.poutput('Loading records...')
        records = self.get_records()
        self.study_records = records
        self.poutput(len(self.study_records))
        self.poutput('Ok')

    # FIELDS

    def do_show_fields(self, _):
        for key in self.study_fields.keys():
            value = self.study_fields[key]
            self.poutput('{}: {}'.format(key, value['field_label']))
        self.poutput('Ok')

    def do_count_fields(self, _):
        self.poutput(len(self.study_fields))
        self.poutput('Ok')

    # RECORDS

    def do_show_records(self, _):
        """
        Usage: show_records
        Show all records in currently selected study.
        """
        for key in self.study_records.keys():
            value = self.study_records[key]
            self.poutput('{}: {}'.format(key, value))
        self.poutput('Ok')

    def do_show_record_data(self, record_id):
        """
        Usage: show_record_data <record_id>
        Show all non-empty field values of given record <record_id>. If fields have never been given a value, these
        fields will not exist. To see a list of fields that are still empty, use the command show_missing_record_data.
        """
        self.get_record_data(record_id)
        self.poutput('Ok')

    def do_show_missing_record_data(self, record_id):
        """
        Usage: show_missing_record_data <record_id>
        Show a list of fields in record <record_id> that have never been given a value. These values are missing and
        can be used to get an idea about which fields still need to be filled.
        """
        self.show_missing_record_data(record_id)
        self.poutput('Ok')

    def do_show_missing_data(self, _):
        """
        Usage: show_missing_data
        For each field defined in the currently selected study show how many records have a missing value for this
        field. Warning: this command can take a very long time to finish!
        """
        nr_records = len(self.study_records)
        missing_fields = {}
        for record_id in self.study_records.keys():
            self.poutput('Processing record {}...'.format(record_id))
            # A side-effect of the show_missing_record_data method is that it returns a list of names
            # of fields that are missing in the record
            fields_names = self.show_missing_record_data(record_id, verbose=False)
            for _name in fields_names:
                if _name not in list(missing_fields.keys()):
                    missing_fields[_name] = 0
                missing_fields[_name] = missing_fields[_name] + 1
        for _name in missing_fields.keys():
            self.poutput('{}: {} / {}'.format(_name, missing_fields[_name], nr_records))

    @with_argument_list()
    def do_find_records(self, args):
        self.poutput('Ok')

    def do_count_records(self, _):
        """
        Usage: count_records
        Count the number of records in the currently selected study.
        """
        self.poutput(len(self.study_records))
        self.poutput('Ok')


if __name__ == '__main__':
    import sys
    shell = CastorRESTClientShell()
    shell.do_connect('{} {}'.format(CLIENT_ID, CLIENT_SECRET))
    shell.do_show_studies(None)
    shell.do_select_study('3')
    # shell.do_show_missing_record_data('T0001')
    # shell.do_show_record_data('T0763')
    shell.do_show_missing_data(None)
    sys.exit(shell.cmdloop())
