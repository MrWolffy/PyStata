import funclib
import pandas as pd
import re
import pyreadstat
from util import *


class StataInterpreter:
    def __init__(self):
        pass

    @staticmethod
    def getinput() -> str:
        return input('. ')

    @staticmethod
    def parse(command: str) -> tuple:
        # parse 'by'
        tmp = re.search(r'by\s+(.+)\s*:', command)
        if tmp is not None:
            by = re.split(r'\s', tmp.group(1))
            command = re.sub(r'by\s+(.+)\s*:', '', command)
        else:
            by = None
        # parse 'option'
        tmp = re.search(r',\s*(.+)', command)
        if tmp is not None:
            option = re.split(r'\s', tmp.group(1))
            command = re.sub(r',\s*(.+)', '', command)
        else:
            option = []
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


class StataPlatform:
    def __init__(self):
        self.data = pd.DataFrame()
        self.meta = pyreadstat._readstat_parser.metadata_container()
        self.macro = {}
        self.r = {}
        self.globals = {}
        self.interpreter = StataInterpreter()

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
            command = self.interpreter.getinput()
            try:
                by, command, args, _if, _in, weight, option = self.interpreter.parse(command)
                print('call %s by using by=%s, args=%s, if=%s, in=%s, weight=%s, option=%s' %
                      (str(command), str(by), str(args), str(_if), str(_in), str(weight), str(option)))
            except SyntaxError as e:
                print_red(e.msg)
                continue
            try:
                self.__getattribute__(command)
            except AttributeError:
                try:
                    self.__setattr__(command, eval('funclib.' + command))
                except AttributeError:
                    print_red('no command named \'%s\'' % command)
                    continue
            # try:
            #     self.__dict__[command](self, args,
            #                            by=by, _if=_if, _in=_in, weight=weight, option=option)
            # except BaseException as e:
            #     print_red(e.args)
            self.__dict__[command](self, args,
                                   by=by, _if=_if, _in=_in, weight=weight, option=option)


if __name__ == '__main__':
    s = StataPlatform()
    s.run()
