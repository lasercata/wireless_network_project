#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Main file'''

##-Imports
from src.utils import *
from src.decode import DecodeMatrix, payload_to_str, test_decode_all_PBCH, test_decode_all_PDCCHU, test_decode_all_payloads
from tests.tests_hamming import *
from tests.tests_modulation import *

from sys import argv
from sys import exit as sysexit

##-Main
def test_matrix():
    m1 = get_matrix('data/tfMatrix.csv')
    # m2 = get_matrix('data/tfMatrix_2.csv')
    # m3 = get_matrix('data/tfMatrix_3.csv')

    print(m1[4][8])
    i, j = unflatten_index(4*624+8)
    print(m1[i][j])

    # print_matrix(m1)
    power_distrib_graph(m1)

    # data = np.genfromtxt('data/tfMatrix.csv', delimiter=';')
    # m2 = data[:,0::2] + 1j * data[:,1::2] # Merges the real and imaginary part of the signal
    # power_distrib_graph(m2)
    pass

def run_tests(matrix, display=True):
    '''Run tests'''

    if display:
        power_distrib_graph(matrix)

    test_hammingDecode()

    test_bpsk()
    test_qpsk()
    print('bpsk and qpsk tests passed')
    test_qam16()
    print('qam16 tests passed')

    print('-'*16)
    print('Testing decode:')
    test_decode_all_PBCH(matrix)
    test_decode_all_PDCCHU(matrix)

    test_decode_all_payloads(matrix)

def print_help(argv):
    '''Prints the help message for the parser and exits.'''

    print(f'Usage: {argv[0]} [-v] [-t] matrix_filename [user_ident]')
    print(f'\nExamples:')
    print(f'    To decode for user 3:                  {argv[0]} data/tfMatrix.csv 3')
    print(f'    To decode for user 3 and show more:    {argv[0]} data/tfMatrix.csv 3 -v')
    print(f'    To decode for all users:               {argv[0]} data/tfMatrix.csv')
    print(f'    To run all tests:                      {argv[0]} data/tfMatrix.csv -t')
    sysexit()

def parser(argv):
    '''Defines a very simple commandline parser for the project.'''

    if len(argv) <= 1 or '-h' in argv or '--help' in argv:
        print_help(argv) # also exists

    testing = False
    if '-t' in argv:
        testing = True

        del argv[argv.index('-t')]

    verbose = False
    if '-v' in argv:
        verbose = True

        del argv[argv.index('-v')]

    if argv[1][0] == '-':
        print(f'Invalid argument "{argv[1]}"')
        sysexit()

    fn = argv[1]
    try:
        m = get_matrix(fn)
    except FileNotFoundError:
        print(f'File "{fn}" not found !')
        sysexit()

    if testing:
        run_tests(m)

    elif len(argv) == 2: # Show all users
        test_decode_all_payloads(m)

    else:
        user_ident = int(argv[2])

        d = DecodeMatrix(m)
        payload = d.get_payload_user(user_ident)
        res = payload_to_str(payload, user_ident)

        if verbose:
            print('PBCHU:', d.decode_PBCH_user(user_ident))
            print('PDCCHU:', d.decode_PDCCHU_user(user_ident))
            print()

        print(res)

##-Run
if __name__ == '__main__':
    parser(argv)
