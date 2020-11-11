import pandas as pd


class CastorClient(object):

    def __init__(self):

        self.df = None
        self.dd = None
        self.op = None

    def load_export_excel(self, excel_file):

        self.df = pd.read_excel(excel_file, sheet_name='Study results')
        self.df.columns = self.df.columns.str.replace(' ', '_')
        self.dd = pd.read_excel(excel_file, sheet_name='Study variable list')
        self.dd.columns = self.dd.columns.str.replace(' ', '_')
        self.op = pd.read_excel(excel_file, sheet_name='Field options')
        self.op.columns = self.op.columns.str.replace(' ', '_')

        self.update_column_data_types()

    def update_column_data_types(self):
        pass

    def convert_columns_int_to_str(self):
        pass

    def convert_date_columns_to_str(self, columns):
        for column in columns:
            if self.df[column].dtype == 'datetime64[ns]':
                self.df[column] = df[column].dt.strftime('%d-%m-%Y')

    def is_unique_key(self, key_columns):
        """
        Checks whether records can be uniquely identified using key_columns. For example,
        Using a SAP number and surgery date you should be able to uniquely identify each
        record in the currently selected Castor study.
        :param key_columns: Column combination that unique identifies a record.
        :return: True/False
        """
        pass
