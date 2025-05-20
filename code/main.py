#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Main file'''

##-Imports
from src.utils import *
from src.decode import test as test_decode #TODO: remove this in the future
from src.decode import test_2 as test_decode_2 #TODO: remove this in the future
from tests.tests_hamming import *
from tests.tests_modulation import *

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

##-Run
if __name__ == '__main__':
    # test_matrix()

    test_hammingDecode()

    test_bpsk()
    test_qpsk()
    print('bpsk and qpsk tests passed')
    test_qam16()
    print('qam16 tests passed')

    print('-'*16)
    print('Testing decode (user_ident = 16):')
    test_decode(16)
    test_decode(9)
    # print('Testing decode:')
    test_decode(12)

    test_decode_2()

