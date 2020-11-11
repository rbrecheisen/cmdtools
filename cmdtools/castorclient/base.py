import os
import datetime
import numpy as np
import pandas as pd


class CastorClient(object):

    def __init__(self):

        self.df = None
        self.dd = None
        self.op = None

    def load_export_excel(self, excel_file):
        """
        Load Castor export file as date frame, data dictionary and option list.
        :param excel_file: Castor export file path.
        :return:
        """
        self.df = pd.read_excel(excel_file, sheet_name='Study results')
        self.df.columns = self.df.columns.str.replace(' ', '_')
        self.dd = pd.read_excel(excel_file, sheet_name='Study variable list')
        self.dd.columns = self.dd.columns.str.replace(' ', '_')
        self.op = pd.read_excel(excel_file, sheet_name='Field options')
        self.op.columns = self.op.columns.str.replace(' ', '_')

    def convert_columns_int_to_str(self, columns):
        """
        Convert given columns from integer to string values.
        :param columns: List of columns to convert.
        :return:
        """
        if isinstance(columns, str):
            columns = [columns]
        for column in columns:
            new_values = []
            for v in self.df[column].values:
                if not np.isnan(v):
                    new_values.append(str(int(v)))
                else:
                    new_values.append(None)
            self.df[column] = pd.Series(data=new_values, dtype=object)

    def convert_date_columns_to_str(self, columns):
        """
        Convert list of columns from date type to string format (dd-mm-yyyy).
        If column is object type, then try to convert each value individually
        to a stringified date format.
        :param columns: List of columns to convert.
        :return:
        """
        if isinstance(columns, str):
            columns = [columns]
        date_format = '%d-%m-%Y'
        for column in columns:
            if self.df[column].dtype == 'datetime64[ns]':
                self.df[column] = self.df[column].dt.strftime(date_format)
            else:
                new_values = []
                for v in self.df[column].values:
                    if isinstance(v, str):
                        new_values.append(v)
                    elif isinstance(v, datetime.datetime):
                        new_values.append(v.strftime(date_format))
                    else:
                        new_values.append(None)
                self.df[column] = pd.Series(data=new_values)

    def show_empty_values_for_column(self, column):
        """
        Shows record IDs that have an empty value for the given column.
        :param column: Column to check.
        :return:
        """
        for _, row in self.df.iterrows():
            record_id = row['Record_Id']
            if row[column] is None:
                print(record_id)

    def is_unique_key(self, columns):
        """
        Checks whether records can be uniquely identified using key_columns. For example,
        Using a SAP number and surgery date you should be able to uniquely identify each
        record in the currently selected Castor study.
        :param columns: Column combination that unique identifies a record.
        :return: True/False
        """
        keys = []
        is_unique = True
        for _, row in self.df.iterrows():
            key_string = self.create_key_string(row, columns)
            if key_string not in keys:
                keys.append(key_string)
            else:
                print('key_string {} not unique'.format(key_string))
                is_unique = False
        return is_unique

    @staticmethod
    def create_key_string(row, columns):
        key_string = ''
        for i in range(len(columns) - 1):
            x = row[columns[i]]
            if x is None:
                key_string += 'None' + '_'
            else:
                key_string += x + '_'
        x = row[columns[len(columns) - 1]]
        if x is None:
            key_string += 'NaT'
        else:
            key_string += x
        return key_string


if __name__ == '__main__':

    client = CastorClient()
    print('Loading data...')
    client.load_export_excel('{}/Desktop/ESPRESSO_v2.0_DPCA_excel_export_20201111091638.xlsx'.format(os.environ['HOME']))
    print('Converting int columns to string...')
    client.convert_columns_int_to_str(['dpca_verrichting_upn'])
    print('Converting date columns to string...')
    client.convert_date_columns_to_str(['dpca_datok'])
    print('Showing empty values dpca_verrichting_upn...')
    client.show_empty_values_for_column('dpca_verrichting_upn')
    print('Showing empty values dpca_datok...')
    client.show_empty_values_for_column('dpca_datok')
    print('Checking unique key [dpca_verrichting_upn, dpca_datok]...')
    client.is_unique_key(['dpca_verrichting_upn', 'dpca_datok'])
    print('Done')
