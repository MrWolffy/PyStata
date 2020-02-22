from typing import Union, List, Iterable, Tuple, Optional
from pandas import DataFrame, Index
import re


def print_red(message):
    print('\033[1;31m' + repr(message) + '\033[0m')


def parse_varname(name: str, length: int, pos='l') -> str:
    if len(name) > length:
        return name[0:length-2] + '~' + name[-1]
    else:
        return name.ljust(length, ' ') if pos == 'l' else name.rjust(length, ' ')


def parse_number(number, length=8):
    if number < 0:
        return re.sub(r'-( +)', r'\1-', '-' + parse_number(abs(number), length=length-1))
    elif 0.1 < abs(number) < 1:
        return (('%%.%df' % (length - 1)) % number)[1:length+1]
    elif number > 10 ** (length - 1):
        return ('%%%d.3g' % length) % number
    else:
        return ('%%%d.%dg' % (length, length - 1)) % number


def get_varlist(vars: List[str], data: DataFrame) -> Union[List[str], Index]:
    if vars:
        try:
            _ = [data[arg] for arg in vars]
            return vars
        except ValueError as e:
            raise SyntaxError('variable %s not found' % e.args[0][:e.args[0].index(' ')])
    return data.columns


def check_args(args: List[str]):
    if args:
        raise SyntaxError('%s not allowed' % args[0])


def check_by(by: Optional[List[str]]):
    if by is not None:
        raise SyntaxError(' may not be combined with by')


def check_if(_if: Optional[str]):
    if _if is not None:
        raise SyntaxError('if not allowed')


def check_in(_in: Optional[Tuple[int, int]]):
    if _in is not None:
        raise SyntaxError('in range not allowed')


def check_weight(weight: Optional[str]):
    if weight is not None:
        raise SyntaxError('weights not allowed')


def check_option(option: List[str]):
    if option:
        raise SyntaxError('option %s not allowed' % option[0])


def split_data(data: DataFrame, _in: Optional[Tuple[int, int]],
               _if: Optional[str], by: Optional[List[str]]) \
        -> Union[DataFrame, Iterable[DataFrame]]:
    if _in is not None:
        data = data[_in[0]:_in[1]]
    if _if is not None:
        pass
    if by is not None:
        pass
    return data



