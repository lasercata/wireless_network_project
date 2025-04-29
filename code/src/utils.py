#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''TODO'''

##-Imports
import numpy as np
import math

# To display T/F matrix
import matplotlib.pyplot as plt
from matplotlib import ticker, cm

# Unit testing
import pytest

# Convolutional decoder
import sk_dsp_comm.fec_conv as fec


##-Functions
def get_matrix(fn: str) -> list[list[np.complex128]]:
    '''
    Parse the csv file `fn` and return the associated matrix.

    - fn : TODO
    '''

    #---Read from file
    data = np.genfromtxt(fn, delimiter=';')

    mat_complex = data[:,0::2] + 1j * data[:,1::2] # Merges the real and imaginary part of the signal

    #---Remove the unused part (only 624 subcarriers are allocated)
    N_Re = 624
    N = 1024

    bound_1 = N_Re // 2 - 1
    bound_2 = N - (N_Re // 2)

    # The short matrix is from range [0 : bound_1] + [bound_2 : ]
    # print(f'1 : {bound_1} ; {bound_2 + 1} : {N}')

    a = [
        [mat_complex[i][j] for j in range(bound_1)]
        + [mat_complex[i][j] for j in range(bound_2, N)]
        for i in range(12)
    ]

    # tf_mat_short = np.array(a)
    return a


def print_matrix(m):
    '''
    Prints the matrix `m`

    - m : TODO
    '''

    # mx_r = 0
    # mx_i = 0

    print('[')
    for i in range(len(m)):
        print('  [', end='')

        for j in range(len(m[i])):
        # for j in range(10):
            real = m[i][j].real
            im = m[i][j].imag

            # if real > mx_r:
            #     mx_r = real
            # if im > mx_i:
            #     mx_i = im

            print(f'{format(round(real, 2), ".02")} + {format(round(im, 2), ".02")}j', end=', ')

        print('\b\b  \b\b],')
    print(']')

    # print(f'max real : {mx_r}')
    # print(f'max imag : {mx_i}')
    pass

def power_distrib_graph(Z):
    '''
    Draws the power distribution graph.

    - Z : the matrix
    '''

    fig, ax = plt.subplots()
    cs = ax.contourf(np.linspace(0, len(Z[0]), len(Z[0])), np.linspace(0, len(Z), len(Z)), np.abs(Z) **2)
    cbar = fig.colorbar(cs)

    ax.set_title('??')
    ax.set_xlabel('frequency')
    ax.set_ylabel('time')

    plt.show()

def flatten_index(i: int, j: int, width: int = 624) -> int:
    """Returns the flatten index of the (i, j) element in the flattened matrix.

    Args:
        i (int): index of the list in the list.
        j (int): index of the element in the list.
        width (int, optional): length of the lists in the list. Defaults to 624.

    Returns:
        int: index of the element in the flatten matrix. 
    """

    return width*i + j

def unflatten_index(i: int, width: int = 624) -> tuple[int, int]:
    """Returns the coordinates of the i element in the unflattened matrix.

    Args:
        i (int): index of the element in the flattened matrix.
        width (int, optional): length of the lists in the list. Defaults to 624.

    Returns:
        tuple[int, int]: coordinates of the element in the unflattened matrix.
    """

    return (i // width, i % width)

def bin2dec(nb: list[int]) -> int:
    """Converts a number from base 2 to base 10.

    Args:
        nb (list[int]): the number in base 2.

    Returns:
        int: number in base 10.
    """

    return int(''.join(str(k) for k in nb), 2)