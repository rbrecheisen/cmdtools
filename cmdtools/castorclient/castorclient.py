import os
import cmd2

INTRO = """
Welcome to the Castor Client!
------------------------------
This tool allows you to analyze Castor study data using its export Excel file.

Type 'help' to show a short list of commands. To view a more extensive list of commands and their descriptions, 
type 'cheat_sheet'.
"""

PROMPT = '(client) '

CHEAT_SHEET = """

General info:
-------------
The Castor client allows you to analyze Castor export Excel files. To view the full list of commands you
can apply, type 'cheat_sheet'.

Result sets:
------------
The client works on the basis of result sets. When you first load an export Excel file it will 
be stored as the first (and current) result set. You can perform a number of operations on a result set
like showing its columns (show_columns command) or showing a field's data type (show_field_type <name>
command). When you actually change the result set, for example by sorting it, the client tool will create
a new result set and set that one to be the current result set. For this reason, make sure you know which
result set you are working on. You can view all result sets using the command show_results. It will display
each result set's name and a short description. You can change these descriptions to something more memorable
using the command: 

    set_result_desc <name>=<description>

General:
--------
- cheat_sheet                       Show this cheat sheet.
- cd <dir path>                     Change the working directory to <dir path>.
- pwd                               Print the working (current) directory.
- shell <shell command>             Run a shell command by preceding it with ! (exclamation mark). For example, to view the
                                    contents of the $HOME environment variable, type !echo $HOME.

Loading/saving data:
-------------
- load_castor_export <file path>    Load Castor export Excel file. You can either specify a single file name, in
                                    which case the file is assumed to be located in the current working directory.
                                    Or you can specify the full path to the file. 

                                    Note that the Castor client expects the sheets in the Excel file with the 
                                    following names:

                                        - Study results
                                        - Study variable list
                                        - Field options

- load_excel <file path>            Load general Excel file. This can be useful if you need some data that you can use
                                    as input to one of the analysis commands. For example, you might load a list of
                                    hospital IDs from one Excel file and use it to extract specific records from 
                                    the Castor export Excel file.

Displaying data:
----------------
- show_columns <result name>
- show_column_values <name>
- show_column_options <name>
- show_column_field_type <name>     Show the variable's field type as specified in the Castor CRF. The following 
                                    field types can be recognized by the Castor client:

                                        - dropdown
                                        - radio
                                        - year
                                        - string
                                        - textarea
                                        - calculation
                                        - numeric
                                        - date

Result sets:
------------
- show_results                      Show all result sets. For each result set, its name and description is given. Also
                                    the number of rows and columns is displayed so you can see the effect of filtering
                                    operations (using the query command) 

- set_current_result <result name>  Set <result name> to be the current result set. Any display or analysis commands
                                    you run will be applied to the current result set. When you load data for the first
                                    time it will automatically become the current result set and will be named 'result_0'.

- set_result_desc <name=desc>       Set the description of the result set <name> to <desc>. By default the description
                                    of a result set will be empty, except for result_0 which will be 'original dataset'.
                                    Query and sort operations, that generate new result sets, will be have descriptions
                                    'query' and 'sort' respectively but you are encouraged to change the description to
                                    something more memorable. Note that the description will be included in the file
                                    name when you save a result set to file.

                                    Example:

                                        set_result_desc result_0=original dataset with other description

                                    This will set the description of result set 'result_0' to 'original dataset with
                                    other description'.

- save_result <name>                Save the given result set to file. The file name will have the following format:

                                        <name>_<desc>.xlsx

                                    where <desc> will be the description with spaces replaced by underscores. 

Analysis:
---------
- query <query string>              Filter the current result set with the given query string. You can build complex 
                                    query sentences using the 'and' and 'or' operators. You can specify variable values 
                                    depending on their type. You should place string values between double-quotes. 
                                    Numeric values can be typed as is. Date values should be placed between double-quotes
                                    as well. The date string format should conform to 'dd-mm-yyyy'. 
                                    Use == as the *equals* operator (do not use = which means assignment)

                                    Example query string:

                                        dob < "01-01-1940" and gender == 1

                                    This expression searches for records corresponding to patients born before 
                                    01-01-1940 and have gender '1' (Male). Note that options are often encoded as numbers, 
                                    like was done here with gender. You can find out which numbers have been assigned to
                                    option values by typing (if you're dataset contains this variable and it is an option
                                    group): 

                                        show_options gender

                                        (0, 'Female')
                                        (1, 'Male')
                                        (9, 'Unknown')

                                    This will list the option values for the option group 'dob'. Not only the names of
                                    these values will be given (male, female, unknown, etc.) but also their numeric code.

                                    The result of the query will be stored in a new result set. This result set will be set to be
                                    the current result set.

- sort <column names> [--asc=0|1]

"""


class CastorClient(object):

    def __init__(self, client_shell):
        super(CastorClient, self).__init__()
        self.client_shell = client_shell  # used for printing output
        self.df = None
        self.dd = None
        self.op = None
        self.current_dir = os.path.abspath(os.path.curdir)
        self.results = {}
        self.current_result = 'result_0'
        self.result_idx = -1

    def next_result_idx(self):
        self.result_idx += 1
        return self.result_idx

    def lookup_column_type(self, column):
        for idx, row in self.dd.iterrows():
            if row['Variable name'] == column:
                field_type = row['Field type']
                if field_type == 'dropdown' or field_type == 'radio' or field_type == 'year':
                    return field_type, 'Int64'
                if field_type == 'string' or field_type == 'textarea' or field_type == 'calculation':
                    return field_type, 'object'
                if field_type == 'numeric':
                    return field_type, 'float64'
                if field_type == 'date':
                    return field_type, 'datetime64'
                self.client_shell.poutput('Unknown field type {}'.format(field_type))
        return None, None

    def load_castor_export(self, excel_file):
        self.client_shell.poutput('Loading {}...'.format(excel_file))
        if excel_file is None or excel_file is '':
            self.client_shell.poutput('Specify the name of the Excel file (as stored in the current directory) or the full file path to the Excel file')
            return
        if not os.path.isfile(excel_file):
            excel_file = os.path.join(self.current_dir, excel_file)
        if not os.path.isfile(excel_file):
            self.client_shell.poutput('File path {} does not exist. Please make sure the current directory and Excel file name are correct')
            return
        self.df = pd.read_excel(excel_file, sheet_name='Study results')
        self.df.columns = df.columns.str.replace(' ', '_')
        self.dd = pd.read_excel(excel_file, sheet_name='Study variable list')
        self.dd.columns = df.columns.str.replace(' ', '_')
        self.op = pd.read_excel(excel_file, sheet_name='Field options')
        self.op.columns = df.columns.str.replace(' ', '_')
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [self.df, 'Original']
        pb = ProgressBar(total=len(self.df.columns)-1, prefix='Progress:', suffix='Finished', decimals=0, length=50, fill='#', zfill='-')
        pb.print_progress_bar(1)
        count = 2  # otherwise the progress bar does not end with 100%
        for column in self.df.columns:
            _, data_type = self.lookup_column_type(column)
            if data_type is not None:
                self.df[column] = pd.Series(self.df[column], dtype=data_type)
                count += 1
                pb.print_progress_bar(count)
        self.client_shell.poutput('Loading done')

    def load_excel(self, excel_file):
        self.client_shell.poutput('Loading {}...'.format(excel_file))
        if excel_file is None or excel_file is '':
            self.client_shell.poutput('Specify the name of the Excel file (as stored in the current directory) or the full file path to the Excel file')
            return
        if not os.path.isfile(excel_file):
            excel_file = os.path.join(self.current_dir, excel_file)
        if not os.path.isfile(excel_file):
            self.client_shell.poutput('File path {} does not exist. Please make sure the current directory and Excel file name are correct')
            return
        df = pd.read_excel(excel_file)
        df.columns = df.columns.str.replace(' ', '_')
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [df, 'Other']
        self.client_shell.poutput('Loading done')

    def show_columns(self, result_name):
        if result_name == '':
            df = self.results[self.current_result][0]
        else:
            df = self.results[result_name][0]
        for column in df.columns:
            self.client_shell.poutput('{}:\t{}'.format(column, df[column].dtype))

    def show_column_values(self, column_name):
        df = self.results[self.current_result][0]
        if column_name not in list(df.columns):
            self.client_shell.poutput('Column {} not present in result set {}'.format(column_name, self.current_result))
            return
        for x in df[column_name].tolist():
            self.client_shell.poutput(x)

    def show_column_options(self, col_name):
        if col_name == '':
            self.client_shell.poutput('Please specify a non-empty column name')
            return
        group_names = self.op['Option group name'].values
        if col_name in group_names:
            for idx, row in self.op.iterrows():
                row_var_name = row['Option group name']
                if row_var_name == col_name:
                    self.client_shell.poutput((row['Option value'], row['Option name']))
        else:
            self.client_shell.poutput('Column {} is not an option group or does not exist!'.format(col_name))

    def show_column_field_type(self, col_name):
        if col_name == '':
            self.client_shell.poutput('Please specify a non-empty column name')
            return
        field_type, _ = self.lookup_column_type(col_name)
        self.client_shell.poutput(field_type)

    def set_current_result(self, result_name):
        if result_name not in list(self.results.keys()):
            self.client_shell.poutput('Result "{}" does not exist. Please specify an existing one'.format(result_name))
            self.show_results()
            return
        self.current_result = result_name
        self.show_results()

    def set_result_desc(self, arg):
        items = [x.strip() for x in arg.split('=')]
        result_name, description = items[0], items[1]
        if result_name in list(self.results.keys()):
            if result_name == 'result_0':
                description = '{} ({})'.format(description, 'Original')
            self.results[result_name][1] = description
        else:
            self.client_shell.poutput('Result "{}" does not exist. Pick an existing result set:'.format(result_name))
        self.show_results()

    def show_results(self):
        if len(self.results.keys()) == 0:
            self.client_shell.poutput('No results available. Please load dataset first')
            return
        for name in self.results.keys():
            current = ''
            if name == self.current_result:
                current = '[current]'
            self.client_shell.poutput('name: {}\t(rows, cols): {}\t{}\t{}'.format(
                name, self.results[name][0].shape, self.results[name][1], current))

    def save_result(self, result_name):
        if result_name == '':
            self.client_shell.poutput('Result name cannot be empty or None. Pick one of the results below:')
            self.show_results()
            return
        if result_name in list(self.results.keys()):
            f = os.path.join(self.current_dir, '{}.xlsx'.format(result_name))
            self.save_df(self.results[result_name][0], f)
            self.client_shell.poutput('Saved data frame "{}" to {}'.format(result_name, f))
        else:
            self.client_shell.poutput('Result name "{}" unknown. Pick one of the results below:')
            self.show_results()

    @staticmethod
    def save_df(df, output_file):
        writer = pd.ExcelWriter(output_file, date_format='DD-MM-YYYY', datetime_format='DD-MM-YYYY')
        df.to_excel(writer, index=False)
        writer.close()

    def query(self, query_string):
        if query_string == '':
            self.client_shell.poutput('Please specify a non-empty query string!')
            return
        df = self.results[self.current_result][0]
        result = df.query(query_string)
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [result, 'Query result']
        self.current_result = result_name
        self.client_shell.poutput('Stored results in result set "{}" (now current result)'.format(result_name))

    def sort(self, columns, ascending):
        if len(columns) == 0:
            self.client_shell.poutput('Please provide a column name or a non-empty list of column names')
            return
        if isinstance(columns, str):
            columns = [columns]
        self.client_shell.poutput('Sorting by columns {} with ascending = {}'.format(columns, ascending))
        df = self.results[self.current_result][0]
        result = df.sort_values(by=columns, ascending=ascending)
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [result, 'Sort result']
        self.current_result = result_name
        self.client_shell.poutput('Stored results in result set "{}" (now current result)'.format(result_name))

    def drop_columns(self, columns):
        if len(columns) == 0:
            self.client_shell.poutput('Please provide a column name or a non-empty list of column names')
            return
        if isinstance(columns, str):
            columns = [columns]
        df = self.results[self.current_result][0]
        result = df.drop(columns, inplace=False)
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [result, 'Dropped']
        self.current_result = result_name
        self.client_shell.poutput('Stored results in result set "{}" (now current result)'.format(result_name))

    def select_columns(self, columns):
        if len(columns) == 0:
            self.client_shell.poutput('Please provide a column name or a non-empty list of column names')
            return
        df = self.results[self.current_result][0]
        result = df[columns]
        result_name = 'result_{}'.format(self.next_result_idx())
        self.results[result_name] = [result, 'Selected']
        self.current_result = result_name
        self.client_shell.poutput('Stored results in result set "{}" (now current result)'.format(result_name))


class CastorClientShell(cmd2.Cmd):

    def __init__(self):
        super(CastorClientShell, self).__init__()
        self.intro = INTRO
        self.prompt = PROMPT
        self.client = CastorClient(self)

    # DOCUMENTATION

    def do_cheat_sheet(self, _):
        self.poutput(CHEAT_SHEET)

    # FILE AND DIRECTORY NAVIGATION

    def do_cd(self, line):
        if line == '.' or line == '':
            self.do_pwd(None)
            return
        if line == '..':
            self.client.current_dir = os.path.split(self.client.current_dir)[0]
            self.do_pwd(None)
            return
        if not os.path.isdir(line):
            line = os.path.join(self.client.current_dir, line)
            if not os.path.isdir(line):
                self.poutput('Directory {} is not a valid directory'.format(line))
                return
        self.client.current_dir = line
        self.do_pwd(None)

    def do_pwd(self, _):
        self.poutput(self.client.current_dir)

    # SYSTEM COMMANDS

    def do_shell(self, line):
        if line is None or line is '':
            print('Please specify a shell command preceded by! For example, !echo $HOME')
            return
        self.poutput('Running shell command: {}'.format(line))
        output = os.popen(line).read()
        self.poutput(output)

    # LOADING DATA

    def do_load_castor_export(self, excel_file):
        excel_file = '/Users/Ralph/Desktop/ESPRESSO_v2.0_DPCA_excel_export_20201027104523.xlsx'
        self.client.load_castor_export(excel_file)

    def do_load_excel(self, excel_file):
        excel_file = '/Users/Ralph/Desktop/PPPD-Whipple 2009-2019 volledige lijst Marjolein.xlsx'
        self.client.load_excel(excel_file)

    # DISPLAYING DATA

    def do_show_columns(self, result_name=''):
        self.client.show_columns(result_name)

    def do_show_column_values(self, col_name):
        self.client.show_column_values(col_name)

    def do_show_column_options(self, col_name):
        self.client.show_column_options(col_name)

    def do_show_column_field_type(self, col_name):
        self.client.show_column_field_type(col_name)

    # RESULT SETS

    def do_show_results(self, _):
        self.client.show_results()

    def do_set_current_result(self, result_name):
        self.client.set_current_result(result_name)

    def do_set_result_desc(self, line):
        self.client.set_result_desc(line)

    def do_save_result(self, result_name):
        self.client.save_result(result_name)

    # PROCESSING AND ANALYSIS

    def do_query(self, query_string):
        self.client.query(query_string)

    def do_sort(self, line):
        columns = []
        ascending = True
        items = [x.strip() for x in line.split(',')]
        if '--ascending=' in items[-1]:
            x = items[-1].split(' ')[0]
            y = items[-1].split(' ')[1]
            v = [x.strip() for x in y.split('=')][1]
            ascending = True if v == '1' or v == 'true' or v == 'True' else False
            columns = items[:-1]
            columns.append(x)
        self.client.sort(columns, ascending)

    def do_drop_columns(self, columns):
        columns = columns.args
        columns = [x.strip() for x in columns.split(',')]
        self.client.drop_columns(columns)

    def do_select_columns(self, columns):
        columns = columns.args
        columns = [x.strip() for x in columns.split(',')]
        self.client.select_columns(columns)


if __name__ == '__main__':
    import sys
    shell = CastorClientShell()
    sys.exit(shell.cmdloop())
