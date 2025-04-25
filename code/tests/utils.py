#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##-Colored output
def cprint(txt: str, col=None, bold=False):
    '''
    Prints `txt` in the given color.

    - txt  : the text to color print ;
    - col  : the color to give to the text ;
    - bold : if True, print the text in bold.
    '''

    if bold:
        txt = '\033[1m' + txt + '\033[0m'

    if col == 'green':
        txt = '\033[32m' + txt + '\033[0m'
    elif col == 'red':
        txt = '\033[31m' + txt + '\033[0m'
    elif col == 'blue':
        txt = '\033[34m' + txt + '\033[0m'
    elif col == 'yellow':
        txt = '\033[33m' + txt + '\033[0m'
    elif col == 'cyan':
        txt = '\033[36m' + txt + '\033[0m'

    print(txt)

def err_print(txt: str):
    '''
    Print `txt` with error color (red)

    - txt : the text to print in error color.
    '''

    cprint(txt, 'red')

def good_print(txt: str):
    '''
    Print `txt` with 'good' color (green)

    - txt : the text to print in 'good' color.
    '''

    cprint(txt, 'green')

##-Utils
def test_func(func_name: str, expected, func, *args, verbose: bool = True, equals = lambda a, b: a == b) -> bool:
    '''
    Tests the function `func` on the arguments `*args`, and checks that the output is `expected`

    - func_name : the function name (for the prints) ;
    - expected  : the expected output given the arguments ;
    - func      : the function ;
    - *args     : the function's arguments ;
    - verbose   : indicate if printing the arguments or not ;
    - equals    : the equality function.
    '''

    if verbose:
        print(f'Testing {func_name}{args} == {expected}')
    else:
        print(f'Testing {func_name}')

    try:
        res = func(*args)
    except Exception as err:
        # if verbose:
        err_print(f'Test failed: the function raised the error {type(err)}: "{err}"')
        # else:
        #     err_print(f'Test failed: the function raised an error')

        return False

    if equals(res, expected):
        good_print('Test passed')
        return True

    else:
        if verbose:
            err_print(f'Test failed: got {func(*args)} instead of {expected} !')
        else:
            err_print('Test failed')

        return False

def test_error(func_name: str, expected_error, func, *args, verbose: bool = True) -> bool:
    '''
    Tests the function `func` on the arguments `*args`, and checks that it raises the error `expected_error`.

    - func_name      : the function name (for the prints) ;
    - expected       : the expected output given the arguments ;
    - expected_error : the expected error raised by the function ;
    - func           : the function ;
    - *args          : the function's arguments ;
    - verbose        : indicate if printing the arguments or not ;
    '''

    if verbose:
        print(f'Testing if {func_name}{args} raises {expected_error}')
    else:
        print(f'Testing {func_name} (should raise {expected_error})')

    try:
        func(*args)
    except Exception as err:
        if type(err) == expected_error:
            good_print('Test passed')
            return True

        else:
            err_print(f'Test failed: raised {err} instead of {expected_error} !')
            return False

    err_print(f'Test failed: the function did not raised the expected error !')
    return False
