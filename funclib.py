from __init__ import StataPlatform
from sys import exit as sysexit
from sys import getsizeof
import numpy as np
import pandas as pd
import pyreadstat
from util import *


def sysuse(self: StataPlatform, args: List[str],
           by: Union[List[str], None], _if: Union[str, None], _in: Union[str, None],
           weight: Union[str, None], option: List[str]):
    """
Title

    [D] sysuse -- Use shipped dataset


Syntax

    Use example dataset installed with Stata

        sysuse ["]filename["] [, clear]


    """
    def check_input():
        # args
        if len(args) > 1:
            raise SyntaxError('invalid %s' % args[1])
        elif len(args) == 0:
            raise SyntaxError('invalid file specification')
        try:
            check_by(by)
        except SyntaxError as e:
            raise SyntaxError('sysuse' + e.msg)
        check_if(_if)
        check_in(_in)
        check_weight(weight)
        # option
        if option:
            if args[0] != 'dir':
                for i, opt in enumerate(option):
                    if i >= 1 or opt != 'clear':
                        raise SyntaxError('option %s not allowed' % opt)
            elif args[0] == 'dir':
                for i, opt in enumerate(option):
                    if i >= 1 or opt != 'all':
                        raise SyntaxError('option %s not allowed' % opt)

    def sysuse_file(dir: str):
        try:
            self.data, self.meta = pyreadstat.read_dta(dir)
            print('(' + self.meta.file_label + ')')
            self.globals['dir'] = dir
        except pyreadstat._readstat_parser.ReadstatError:
            print_red('file \"%s\" not found' % dir)

    def main():
        try:
            check_input()
        except SyntaxError as e:
            print_red(e.msg)
            return
        dir = args[0]
        if dir != 'dir':
            dir = args[0].strip('\"')
            if not dir.endswith('.dta'):
                dir = dir + '.dta'
            sysuse_file(dir)
        else:
            pass

    main()


def describe(self: StataPlatform, args: List[str],
             by: Union[List[str], None], _if: Union[str, None], _in: Union[str, None],
             weight: Union[str, None], option: List[str]):
    """
Title

    [D] describe -- Describe data in memory or in file


Syntax

    Describe data in memory

        describe [varlist] [, options]


    Describe data in file

        describe [varlist] using filename [, options]


    memory_options        Description
    -------------------------------------------------------------------------
    simple                display only variable names
    short                 display only general information
    fullnames             do not abbreviate variable names
    numbers               display variable number along with name
    -------------------------------------------------------------------------


"""
    def check_input():
        try:
            check_by(by)
        except SyntaxError as e:
            raise SyntaxError('describe' + e.msg)
        check_if(_if)
        check_in(_in)
        check_weight(weight)
        # option
        if len(option) > 1 and 'simple' in option:
            raise SyntaxError('simple may not be combined with other options')
        if 'fullnames' in option and 'numbers' in option:
            raise SyntaxError('options numbers and fullnames may not be combined')
        for item in option:
            if item not in ['simple', 'short', 'fullnames', 'numbers']:
                raise SyntaxError('option %s not allowed' % item)

    def describe_simple(list: Iterable[str]):
        for i, var in enumerate(list):
            print(parse_varname(var, 12), end='  ')
            if i % 4 == 3:
                print()

    def describe_short(dir: str, data: pd.DataFrame, size: int, meta):
        print('Contains data from', dir)
        print('obs:'.ljust(6, ' '), format(data.shape[0], ',').rjust(14, ' '),
              ' ' * 18, meta.file_label, sep='')
        print('vars:'.ljust(6, ' '), format(data.shape[1], ',').rjust(14, ' '), sep='')
        print('size:'.ljust(6, ' '), format(size, ',').rjust(14, ' '),
              ' ' * 18, np.where(len(meta.notes) != 0, '(_dta has notes)', ''), sep='')

    def describe_main(data, meta, args, **kwargs):
        # head
        print('-' * 82)
        print('              storage    value')
        print('variable name   type     label      variable label')
        print('-' * 82)
        # body
        for i, var in enumerate(args):
            if kwargs.get('numbers'):
                print(str(i + 1).rjust(4, ' ') + '. ',
                      parse_varname(var, 8) + ' ', end='')
            elif kwargs.get('fullnames'):
                print(var.ljust(16, ' '), end='')
                if len(var) > 15:
                    print('\n' + ' ' * 16, end='')
            else:
                print(parse_varname(var, 15), end=' ')
            print(np.array(data[var][0]).dtype.name.ljust(9, ' '),
                  meta.variable_to_label.get(var, '').ljust(11, ' '),
                  meta.column_labels[np.where(data.columns.values == var)[0][0]], sep='')
        print('-' * 82)

    def describe_using(args, **kwargs):
        try:
            data, meta = pyreadstat.pyreadstat.read_dta(args[-1])
            meta.dir = args[-1]
            kwargs['using'] = True
        except pyreadstat._readstat_parser.ReadstatError:
            print_red('file \"%s\" not found' % args[-1])
            return
        if kwargs.get('simple'):
            describe_simple(data.columns)
            return
        describe_short(meta.dir, data, getsizeof(data.values.copy()), meta)
        if kwargs.get('short'):
            return
        vars = get_varlist(args[:-2], data)
        describe_main(data, meta, vars, **kwargs)

    def describe_(args, **kwargs):
        if kwargs.get('simple'):
            describe_simple(self.data.columns)
            return
        describe_short(self.globals['dir'], self.data, getsizeof(self.data.values.copy()), self.meta)
        if kwargs.get('short'):
            return
        vars = get_varlist(args, self.data)
        describe_main(self.data, self.meta, vars, **kwargs)

    def main():
        try:
            check_input()
        except SyntaxError as e:
            print_red(e.msg)
            return
        kwargs = {}
        for item in option:
            kwargs[item] = True
        try:
            if len(args) >= 2 and args[-2] == 'using':
                describe_using(args, **kwargs)
            else:
                describe_(args, **kwargs)
        except SyntaxError as e:
            print_red(e.msg)

    main()


def exit(self: StataPlatform, args: List[str],
         by: Union[List[str], None], _if: Union[str, None], _in: Union[str, None],
         weight: Union[str, None], option: List[str]):
    """
Title

    [R] exit -- Exit Stata


Syntax

        exit [, clear]


"""

    def check_input():
        check_args(args)
        check_by(by)
        check_if(_if)
        check_in(_in)
        check_weight(weight)
        # option
        for i, item in enumerate(option):
            if item != 'clear' or i >= 1:
                raise SyntaxError('option %s not allowed' % item)
        if self.globals.get('data_has_been_changed') and len(option) == 0:
            raise SyntaxError('no, data in memory would be lost')

    def main():
        try:
            check_input()
        except SyntaxError as e:
            print_red(e.msg)
            return
        sysexit(0)

    main()


def summarize(self: StataPlatform, args: List[str],
              by: Union[List[str], None], _if: Union[str, None], _in: Union[str, None],
              weight: Union[str, None], option: List[str]):
    """
Title

    [R] summarize -- Summary statistics


Syntax

    summarize [varlist] [if] [in] [weight] [, options]

    options           Description
    -------------------------------------------------------------------------
    detail            display additional statistics
    -------------------------------------------------------------------------
    varlist may contain factor variables; see fvvarlist.
    varlist may contain time-series operators; see tsvarlist.
    by, rolling, and statsby are allowed; see prefix.

    aweights, fweights, and iweights are allowed.  However, iweights may not
      be used with the detail option; see weight.


"""




