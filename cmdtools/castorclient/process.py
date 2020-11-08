import pandas as pd
import numpy as np


class ProcessingStep(object):

    def execute(self, df):
        raise NotImplementedError('Implement this method')


class ConvertColumnsFromIntToString(ProcessingStep):

    def __init__(self, column_names):
        if isinstance(column_names, str):
            self.column_names = [column_names]
        else:
            self.column_names = column_names

    def execute(self, df):
        for column_name in self.column_names:
            new_values = []
            for v in df[column_name].values:
                if not np.isnan(v):
                    new_values.append(str(int(v)))
                else:
                    new_values.append(None)
            df[column_name] = pd.Series(data=new_values, dtype=object)
        return df


class ChangeColumnDatesToFormattedString(ProcessingStep):

    def __init__(self, date_format):
        self.date_format = date_format

    def execute(self, df):
        for column in df.columns:
            if df[column].dtype == 'datetime64[ns]':
                df[column] = df[column].dt.strftime(self.date_format)
        return df


class MapDicaToCastorColumnNames(ProcessingStep):

    def __init__(self, mapping_excel_file, key_column, value_column):
        self.mapping_json = self.load_mapping_to_json(mapping_excel_file, key_column, value_column)

    @staticmethod
    def load_mapping_to_json(mapping_file, k, v):
        mapping = pd.read_excel(mapping_file)
        mapping_json = {}
        for _, row in mapping.iterrows():
            if isinstance(row[v], float):
                mapping_json[row[k]] = None
            else:
                mapping_json[row[k]] = row[v]
        return mapping_json

    def execute(self, df):
        new_columns = []
        for column in df.columns:
            new_column = self.mapping_json[column]
            if new_column is not None:
                new_columns.append(new_column)
            else:
                new_columns.append(column)
        df.columns = new_columns
        return df
