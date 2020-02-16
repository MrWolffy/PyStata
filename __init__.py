import pandas
import re


class StataPlatform:
    def __init__(self):
        pass

    @staticmethod
    def parse(command: str):
        # parse 'by'
        tmp = re.search(r'by\s+(.+)\s*:', command)
        if tmp is not None:
            by = tmp.group(1)
            command = re.sub(r'by\s+(.+)\s*:', '', command)
        else:
            by = None
        # parse 'option'
        tmp = re.search(r',\s*(.+)', command)
        if tmp is not None:
            option = re.split(r'\s', tmp.group(1))
            command = re.sub(r',\s*(.+)', '', command)
        else:
            option = None
        # parse 'weight'
        tmp = re.search(r'\[(.+)\]', command)
        if tmp is not None:
            weight = re.sub(r'\s', '', tmp.group(1))
            command = re.sub(r'\[(.+)\]', '', command)
        else:
            weight = None
        # parse 'in'
        tmp = re.search(r'in\s+((\d+)/(\d+))', command)
        if tmp is not None:
            _in = (int(tmp.group(2)), int(tmp.group(3)))
            command = re.sub(r'in\s+(\d+/\d+)', '', command)
        else:
            _in = None
        # parse 'if'
        tmp = re.search(r'if\s+(.+)', command)
        if tmp is not None:
            _if = tmp.group(1).strip()
            command = re.sub(r'if\s+(.+)\s*', '', command)
        else:
            _if = None
        # parse 'command'
        command = command.strip().split()
        if len(command) == 0:
            raise SyntaxError('no command given')
        return by, command[0], command[1:], _if, _in, weight, option

    @staticmethod
    def split(data: pandas.DataFrame, by: str):
        return data

    def run(self):
        welcome = '''
  ___  ____  ____  ____  ____ (R)
 /__    /   ____/   /   ____/
___/   /   /___/   /   /___/          Copyright 1985-2015 StataCorp LP
  Statistics/Data Analysis            StataCorp
                                      4905 Lakeway Drive
                                      College Station, Texas 77845 USA
                                      800-STATA-PC        http://www.stata.com
                                      979-696-4600        stata@stata.com
                                      979-696-4601 (fax)
'''
        print(welcome)
        while True:
            command = input()
            by, command, args, _if, _in, weight, option = self.parse(command)
            print(by, command, args, _if, _in, weight, option)
            # command = eval(command)
            # for data_slice in split(self.data, by=by):
            #     command.__call__(data_slice, args, _if=_if, _in=_in, weight=weight, option=option)


if __name__ == '__main__':
    s = StataPlatform()
    s.run()
