#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Main file'''

##-Imports
from utils import *

##-Main
def test_matrix():
    m1 = get_matrix('data/tfMatrix.csv')
    m2 = get_matrix('data/tfMatrix_2.csv')
    m3 = get_matrix('data/tfMatrix_3.csv')

    # print_matrix(m1)
    power_distrib_graph(m1)

##-Run
if __name__ == '__main__':
    test_matrix()
