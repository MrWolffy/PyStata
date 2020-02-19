from __init__ import StataPlatform
from sys import exit as sysexit
from sys import getsizeof
import re
import numpy as np
import pandas as pd
from scipy import stats
import pyreadstat
from util import *


def sysuse(self: StataPlatform, args: List[str],
           by: Union[List[str], None], _if: Union[str, None], _in: Union[Tuple[int, int], None],
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
             by: Union[List[str], None], _if: Union[str, None], _in: Union[Tuple[int, int], None],
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
         by: Union[List[str], None], _if: Union[str, None], _in: Union[Tuple[int, int], None],
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
              by: Union[List[str], None], _if: Union[str, None], _in: Union[Tuple[int, int], None],
              weight: Union[str, None], option: List[str]):
    """
Title

    [R] summarize -- Summary statistics


Syntax

    summarize [varlist] [if] [in] [weight] [, options]

    options           Description
    -------------------------------------------------------------------------
    detail            display additional statistics
    separator(#)      draw separator line after every # variables; default is
                        separator(5)
    -------------------------------------------------------------------------
    varlist may contain factor variables; see fvvarlist.
    varlist may contain time-series operators; see tsvarlist.
    by, rolling, and statsby are allowed; see prefix.

    aweights, fweights, and iweights are allowed.  However, iweights may not
      be used with the detail option; see weight.


"""

    def check_input():
        for i, opt in enumerate(option):
            if i >= 2 or re.search(opt, r'(detail|seperator\(\d+\))') is None:
                raise SyntaxError('option %s not allowed' % opt)

    def summarize_detail(data, varlist):
        def cal_descriptions(data: pd.Series):
            obs = np.sum(np.logical_and(np.logical_not(list(map(lambda x: isinstance(x, str), data))),
                                        np.logical_not(data == np.nan)))
            if obs == 0:
                return obs
            percentiles = {str(percent) + '%': np.percentile(data, percent, interpolation='higher')
                           for percent in [1, 5, 10, 25, 50, 75, 90, 95, 99]}
            percentiles['50%'] = np.percentile(data, 50, interpolation='linear')
            sorted_value = np.sort(data)
            smallest = sorted_value[:4]
            largest = sorted_value[-4:]
            sum_of_wgt = None
            mean = data.mean()
            stddev = data.std()
            variance = stddev ** 2
            skew = stats.skew(data.values)
            kurt = stats.kurtosis(data.values) + 3
            return percentiles, smallest, largest, obs, sum_of_wgt, mean, stddev, variance, skew, kurt

        for var in varlist:
            vals = cal_descriptions(data[var])
            print(self.meta.column_labels[np.where(data.columns.values == var)[0][0]].center(61, ' '))
            print('-------------------------------------------------------------')
            if vals == 0:
                print('no observations')
            else:
                print('      Percentiles      Smallest')
                print(' 1%%     %s       %s' %
                      (parse_number(vals[0]['1%']), parse_number(vals[1][0])))
                print(' 5%%     %s       %s' %
                      (parse_number(vals[0]['5%']), parse_number(vals[1][1])))
                print('10%%     %s       %s       Obs            %s' %
                      (parse_number(vals[0]['10%']), parse_number(vals[1][2]), parse_number(vals[3])))
                print('25%%     %s       %s       Sum of Wgt.            ' %
                      (parse_number(vals[0]['25%']), parse_number(vals[1][3])))
                print()
                print('50%%     %s                      Mean           %s' %
                      (parse_number(vals[0]['50%']), parse_number(vals[5])))
                print('                        Largest       Std. Dev.      %s' %
                      parse_number(vals[6]))
                print('75%%     %s       %s' %
                      (parse_number(vals[0]['75%']), parse_number(vals[2][0])))
                print('90%%     %s       %s       Variance       %s' %
                      (parse_number(vals[0]['90%']), parse_number(vals[2][1]), parse_number(vals[7])))
                print('95%%     %s       %s       Skewness       %s' %
                      (parse_number(vals[0]['95%']), parse_number(vals[2][2]), parse_number(vals[8])))
                print('99%%     %s       %s       Kurtosis       %s' %
                      (parse_number(vals[0]['99%']), parse_number(vals[2][3]), parse_number(vals[9])))
            print()

    def summarize_(data, varlist):
        def cal_descriptions(data: pd.Series) -> tuple:
            obs = np.sum(np.logical_and(np.logical_not(list(map(lambda x: isinstance(x, str), data))),
                                        np.logical_not(data == np.nan)))
            if obs == 0:
                return obs, None, None, None, None
            mean = data.mean()
            stddev = data.std()
            _min = data.min()
            _max = data.max()
            return obs, mean, stddev, _min, _max

        sep = 5
        for opt in option:
            result = re.search(opt, r'seperator\((\d+\))')
            if result:
                sep = int(result.group(1))
        print('    Variable |        Obs        Mean    Std. Dev.       Min        Max')
        print('-------------+---------------------------------------------------------')
        for i, var in enumerate(varlist):
            vals = cal_descriptions(data[var])
            print(parse_varname(var, 12, 'r'), '|', end='   ')
            print('%s' % parse_number(vals[0]), end='    ')
            if vals[0] != 0:
                print('%s' % parse_number(vals[1]), end='    ')
                print('%s' % parse_number(vals[2]), end='   ')
                print('%s' % parse_number(vals[3]), end='   ')
                print('%s' % parse_number(vals[4]), end='')
            print()
            if (i + 1) % sep == 0:
                print('-------------+---------------------------------------------------------')

    def main():
        check_input()
        data = split_data(self.data, _in, _if, by)
        varlist = get_varlist(args, data)
        if 'detail' in option:
            summarize_detail(data, varlist)
        else:
            summarize_(data, varlist)

    main()






