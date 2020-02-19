from typing import Union, List, Iterable, Tuple
from pandas import DataFrame
import re


def print_red(message):
    print('\033[1;31m' + repr(message) + '\033[0m')


def parse_varname(name: str, length: int, pos='l') -> str:
    if len(name) > length:
        return name[0:length-2] + '~' + name[-1]
    else:
        return name.ljust(length, ' ') if pos == 'l' else name.rjust(length, ' ')


def parse_number(number, length=8):
    if 0.1 < abs(number) < 1:
        return ('%.7f' % number)[1:9]
    elif number > 1e7:
        return '%8.3g' % number
    else:
        return '%8.7g' % number


def get_varlist(vars: List[str], data: DataFrame) -> Iterable:
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


def check_by(by: Union[List[str], None]):
    if by is not None:
        raise SyntaxError(' may not be combined with by')


def check_if(_if: Union[str, None]):
    if _if is not None:
        raise SyntaxError('if not allowed')


def check_in(_in: Union[Tuple[int, int], None]):
    if _in is not None:
        raise SyntaxError('in range not allowed')


def check_weight(weight: Union[str, None]):
    if weight is not None:
        raise SyntaxError('weights not allowed')


def check_option(option: List[str]):
    if option:
        raise SyntaxError('option %s not allowed' % option[0])


def split_data(data: DataFrame, _in: Union[Tuple[int, int], None],
               _if: Union[str, None], by: Union[List[str], None]) \
        -> Union[DataFrame, Iterable[DataFrame]]:
    if _in is not None:
        data = data[_in[0]:_in[1]]
    if _if is not None:
        pass
    if by is not None:
        pass
    return data



