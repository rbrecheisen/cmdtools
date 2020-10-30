import os
import cmd2
import numpy as np


class Result(object):

    def __init__(self, data, name):
        self.data = data
        self.name = name
        self.description = None


class ResultManager(object):

    def __init__(self):
        self.results = {}
        self.current_result = None
        self.result_idx = -1

    def next_result_idx(self):
        self.result_idx += 1
        return self.result_idx

    def add_result_data(self, data):
        name = 'result_{}'.format(self.next_result_idx())
        result = Result(data, name)
        self.results[name] = result
        self.current_result = self.results[name]

    def remove_result_data(self, name):
        self.current_result = self.results['result_0']
        del self.results[name]

    def get_current_result_data(self):
        return self.current_result.data

    def set_current_result(self, name):
        self.current_result = self.results[name]

    def set_result_description(self, name, description):
        self.results[name].description = description

    def undo(self):
        name = self.current_result.name
        index = int(name.split('_')[1])
        index = np.minimum(0, index-1)
        name = 'result_{}'.format(index)
        self.current_result = self.results[name]

    def redo(self):
        name = self.current_result.name
        index = int(name.split('_')[1])
        index = np.maximum(index+1, len(self.results.keys()))
        name = 'result_{}'.format(index)
        self.current_result = self.results[name]

    def show_results(self):
        current = ''
        for result in self.results.values():
            if result.name == self.current_result.name:
                current = '[current]'
            print('{}: description = {} {}'.format(result.name, result.description, current))


class BasicShell(cmd2.Cmd):

    def __init__(self):
        super(BasicShell, self).__init__()
        self.result_manager = ResultManager()
        self.current_dir = os.path.abspath(os.path.curdir)
        self.intro = 'Put your intro inside a global variable INTRO'
        self.cheat_sheet = 'Put your cheat sheet inside a global variable CHEAT_SHEET'
        self.prompt = '(shell) '

    def add_result(self, data):
        self.result_manager.add_result_data(data)

    def remove_result(self, name):
        self.result_manager.remove_result_data(name)

    def do_cheat_sheet(self, _):
        self.poutput(self.cheat_sheet)

    def do_cd(self, line):
        if line == '.' or line == '':
            self.do_pwd(None)
            return
        if line == '..':
            self.current_dir = os.path.split(self.current_dir)[0]
            self.do_pwd(None)
            return
        if not os.path.isdir(line):
            line = os.path.join(self.current_dir, line)
            if not os.path.isdir(line):
                self.poutput('Directory {} is not a valid directory'.format(line))
                return
        self.current_dir = line
        self.do_pwd(None)

    def do_pwd(self, _):
        self.poutput(self.current_dir)

    def do_ls(self, _):
        self.do_shell('ls -lap')

    def do_shell(self, line):
        if line is None or line is '':
            print('Please specify a shell command preceded by! For example, !echo $HOME')
            return
        self.poutput('Running shell command: {}'.format(line))
        output = os.popen(line).read()
        self.poutput(output)

    def do_show_results(self, _):
        self.result_manager.show_results()

    def do_set_result_desc(self, line):
        items = [x.strip() for x in line.split('=')]
        name, description = items[0], items[1]
        self.result_manager.set_result_description(name, description)

    def do_undo(self, _):
        self.result_manager.undo()

    def do_redo(self, _):
        self.result_manager.redo()
