import os
import cmd2
import pydicom

from pydicom.tag import Tag
from pydicom._dicom_dict import DicomDictionary

from cmdtools.lib.shell import BasicShell


INTRO = """
Welcome to the DICOM Explorer!
------------------------------
This tool allows you to explore lots of DICOM files at the same time. Type 'help' to view a short list of
commands. Type 'cheat_sheet' to view a more detailed list of commands.
"""

PROMPT = '(shell) '

CHEAT_SHEET = """
This is the cheat sheet
"""


def is_dicom(file_path):
    if not os.path.isfile(file_path):
        return False
    try:
        with open(file_path, "rb") as f:
            return f.read(132).decode("ASCII")[-4:] == "DICM"
    except:
        return False


class DicomExplorerShell(BasicShell):

    def __init__(self):
        super(DicomExplorerShell, self).__init__()
        self.intro = INTRO
        self.prompt = PROMPT
        self.cheat_sheet = CHEAT_SHEET
        # self.do_load_dir('/Users/ralph/data/RIDER/RIDER-1')

    def do_load_file(self, file_path):
        if not os.path.isfile(file_path):
            file_path = os.path.join(self.current_dir, file_path)
        if not is_dicom(file_path):
            self.poutput('File is not DICOM')
            return
        self.poutput('Loading...')
        self.result_manager.add_result_data([file_path])
        self.poutput('Loading done')

    def do_load_dir(self, dir_path):
        if not os.path.isdir(dir_path):
            dir_path = os.path.join(self.current_dir, dir_path)
        self.poutput('Loading {}...'.format(dir_path))
        data = []
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if not f.startswith('._'):
                    f = os.path.join(root, f)
                    if is_dicom(f):
                        data.append(f)
        self.result_manager.add_result_data(data)
        self.poutput('Loading done')

    def do_show_files(self, _):
        files = self.result_manager.get_current_result_data()
        for f in files:
            self.poutput(f)
        self.do_count_files(None)

    def do_count_files(self, _):
        files = self.result_manager.get_current_result_data()
        self.poutput(len(files))

    def do_dump_file(self, file_name):
        files = self.result_manager.get_current_result_data()
        count = 0
        counted_files = []
        for f in files:
            if file_name in f:
                count += 1
                counted_files.append(f)
        if count == 0:
            if os.path.isfile(file_name):
                p = pydicom.read_file(file_name)
                self.poutput(p)
            else:
                self.poutput('Could not find file {}'.format(file_name))
        elif count == 1:
            p = pydicom.read_file(counted_files[0])
            self.poutput(p)
        elif count > 1:
            self.poutput('Found multiple files with same name:')
            for f in counted_files:
                self.poutput(f)
            self.poutput('Please select full file path of file you want and repeat this command')


if __name__ == '__main__':
    import sys
    shell = DicomExplorerShell()
    sys.exit(shell.cmdloop())
