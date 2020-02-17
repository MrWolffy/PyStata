from typing import Union, List
from __init__ import StataPlatform, print_red
import pandas as pd
import pyreadstat


def sysuse(self: StataPlatform, data: Union[pd.DataFrame, None], args: List[str],
           _if: Union[str, None], _in: Union[str, None], weight: Union[str, None], option: Union[list, None]):
    """
Title

    [D] sysuse -- Use shipped dataset


Syntax

    Use example dataset installed with Stata

        sysuse ["]filename["] [, clear]


    """
    # another syntax should be considered
    # see Stata help
    def check_input(args, _if, _in, weight, option):
        # check input #
        # args
        if len(args) > 1:
            raise SyntaxError('invalid %s' % args[1])
        elif len(args) == 0:
            raise SyntaxError('invalid file specification')
        # if
        if _if is not None:
            raise SyntaxError('if not allowed')
        # in
        if _in is not None:
            raise SyntaxError('in range not allowed')
        # weight
        if weight is not None:
            raise SyntaxError('weights not allowed')
        # option
        if option is not None:
            if args[0] != 'dir':
                for i, opt in enumerate(option):
                    if i >= 1 or opt != 'clear':
                        raise SyntaxError('option %s not allowed' % opt)
            elif args[0] == 'dir':
                for i, opt in enumerate(option):
                    if i >= 1 or opt != 'all':
                        raise SyntaxError('option %s not allowed' % opt)

    def sysuse_file(dir):
        try:
            self.data, self.meta = pyreadstat.read_dta(dir)
            print('(' + self.meta.file_label + ')')
        except pyreadstat._readstat_parser.ReadstatError:
            print_red('file \"%s\" not found' % dir)

    try:
        check_input(args, _if, _in, weight, option)
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






