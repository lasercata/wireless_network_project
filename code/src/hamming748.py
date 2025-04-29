#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''File dealing with the implementation of the Hamming 748 coding scheme'''

##-Imports
import numpy as np

##-Main
class Hamming748:
    '''Class defining the Hamming748 coding scheme.'''

    def __init__(self):
        '''Constructor'''
    
        self.H_ = [
            [0, 0, 0, 1, 1, 1, 1],
            [0, 1, 1, 0, 0, 1, 1],
            [1, 0, 1, 0, 1, 0, 1]
        ]
        self.H = np.array(self.H_)

        # self.no_err = [0, 0, 0]
        # self.one_err = [0, 0, 1]
        # self.

    def encode(self, x: list[int]) -> list[int]:
        '''TODO: Docstring for encode.ERROR main.py::test_error
        - x : TODO
        '''
    
        pass

    def decode(self, y: list[int]) -> list[int]:
        '''
        Decodes `y`.

        - y : the bits to decode. Its length should be a multiple of eight.
        '''

        if len(y) % 8 != 0:
            raise ValueError('The length of `y` must be a multiple of 8')
    
        res = []
        for k in range(len(y) // 8):
            res += self.decode_block(y[k * 8 : (k + 1) * 8])

        return res

    def decode_block(self, y: list[int]) -> list[int]:
        '''
        Decodes `y`.

        - y : the list of 8 bits representing the encoded four bits.

        Returns the decoded and corrected four bits.
        '''
    
        nb_err, err_pos = self._calc_err(y)

        if nb_err >= 2:
            raise ValueError('Packet cannot be corrected, it has to be dropped.')

        if err_pos is not None:
            y[err_pos - 1] = 1 - y[err_pos - 1]

        x = y[:4]
        return x

    def _calc_syndrome(self, y: list[int]) -> list[int]:
        '''
        Calculates the syndrome for `y`.

        - y : the encoded 8 bits.
        '''
    
        y_np = np.array([[k] for k in y[:-1]]) # Transposition of y, removing the last bit
        epsilon = np.matmul(self.H, y_np) # epsilon = H . y_74
        
        synd = np.transpose(epsilon).tolist()[0] # transpose and transform to list[int]
        synd = [b & 1 for b in synd] # Return in Z/2Z

        return synd

    def _check_parity_bit(self, y: list[int]) -> bool:
        '''
        Checks if the parity bit is correct.
        I.e if, in in Z/2Z,
            (b_0 + ... + b_6) = b_7

        - y : the encoded bits (8 bits long)
        '''
    
        return (sum(k for k in y[:-1]) & 1) == y[-1]

    def _calc_err(self, y: list[int]) -> tuple[int, int | None]:
        '''
        Calculates the number of errors found with the syndrome.

        - syndrome   : the syndrome represented as a list of 3 integers ;
        - parity_bit : the parity bit from `y`.

        Return the error number and the error position (if there is one error).
        '''

        syndrome = self._calc_syndrome(y)
    
        # Convert the number represented by syndrome to decimal
        c = int(''.join(str(k) for k in syndrome), 2)

        if c == 0:
            return 0, None

        if self._check_parity_bit(y):
            return 2, None

        return 1, c


