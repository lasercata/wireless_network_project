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

def run_tests():
    '''Run tests'''

    # test_matrix()

    test_hammingDecode()

    test_bpsk()
    test_qpsk()
    print('bpsk and qpsk tests passed')
    test_qam16()
    print('qam16 tests passed')

    print('-'*16)
    print('Testing decode:')
    m1 = get_matrix('data/tfMatrix.csv')
    # m1 = get_matrix('data/tfMatrix_3.csv')
    # power_distrib_graph(m1)

    test_decode_all_PBCH(m1)
    test_decode_all_PDCCHU(m1)

    test_decode_all_payloads(m1)

def print_help(argv):
    '''Prints the help message for the parser and exits.'''

    print(f'Usage: {argv[0]} matrix_filename [user_ident]')
    print(f'Or, to run the tests: {argv[0]} -t')
    print(f'\nExamples:')
    print(f'    To decode for user 3:    {argv[0]} data/tfMatrix.csv 3')
    print(f'    To decode for all users: {argv[0]} data/tfMatrix.csv')
    print(f'    To run all tests:        {argv[0]} -t')
    sysexit()

def parser(argv):
    '''Defines a very simple commandline parser for the project.'''

    if len(argv) <= 1 or '-h' in argv or '--help' in argv:
        print_help(argv) # also exists

    if argv[1].lower() == '-t':
        run_tests()
        sysexit()

    if argv[1][0] == '-':
        print(f'Invalid argument "{argv[1]}"')
        sysexit()

    fn = argv[1]
    try:
        m = get_matrix(fn)
    except FileNotFoundError:
        print(f'File "{fn}" not found !')
        sysexit()

    if len(argv) == 2: # Show all users
        test_decode_all_payloads(m)

    else:
        user_ident = int(argv[2])

        payload = DecodeMatrix(m).get_payload_user(user_ident)
        print(payload_to_str(payload, user_ident))

##-Run
if __name__ == '__main__':
    parser(argv)
