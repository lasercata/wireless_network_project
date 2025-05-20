#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##-Imports
import numpy as np

from src.demod import bpsk_demod, qpsk_demod, qam16_demod
from src.hamming748 import Hamming748
from src.utils import bin2dec, flatten_index, get_matrix

##-Utils
def demod_decode_block(block: list[np.complex128], mcs: int = 0) -> list[int]:
    '''
    Demods (using 2QAM, 4QAM or 16QAM according to `mcs`) and then decodes (using Hamming748) the 48 bits block into a 24 bits block.

    Args:
        :block: the complex block to demod and decode
        :mcs:   an integer indicating which demodulation algorithm to use. Possible values:
                    0 : bpsk, Hamming748
                    1 : not implemented in this project
                    2 : qpsk, Hamming748
                    3 : not implemented in this project
    '''

    if mcs == 0:
        demoded = bpsk_demod(block)

    elif mcs == 1:
        raise NotImplementedError('Not implemented in this project')

    elif mcs == 2:
        demoded = qpsk_demod(block)

    elif mcs == 3:
        raise NotImplementedError('Not implemented in this project')

    else:
        raise ValueError(f'mcs should be in [0 ; 3], but {mcs} was found !')

    h = Hamming748()
    decoded = h.decode(demoded)

    return decoded

##-DecodeMatrix
class DecodeMatrix:
    '''Class defining methods to decode a simplified 5G signal'''

    def __init__(self, matrix: list[list[np.complex128]]):
        '''
        Constructor.

        Args:
            :matrix: the matrix representing the signal
        '''

        self.matrix = matrix
        self.flattened_mat = None

        self.mat_idx = 0

    def retreive_PBCH(self) -> list[np.complex128]:
        '''
        Retreives the PBCH (broadcast channel) from the matrix.
        It also flattens the matrix.

        In fact, it only removes the synchronisation symbols.

        Notes: We only know the beginning of it (third line, or more precisely, the first symbol that is not used for synchronisation).
        The lenght depends on the number of users.

        Returns:
            np.ndarray: the PBCH we retreived
        '''

        pbch_and_more = self.matrix[2:] # The PBCH starts from the third line.

        # Flatten the matrix
        flatten_mat = []
        for i in range(len(pbch_and_more)):
            for j in range(len(pbch_and_more[i])):
                flatten_mat.append(pbch_and_more[i][j])

        self.flattened_mat = flatten_mat
        return flatten_mat

    def decode_PBCH_header(self) -> tuple[int, int]:
        '''
        Decodes the header of the PBCH.

        Returns:
            tuple: (cell ident, number of users).
        '''
    
        header = self.retreive_PBCH()[:48]

        decoded_header = demod_decode_block(header, 0) # 0 for 2qam

        # Retreiving cell ident (18 bits) and user number (6 bits)
        cell_ident = bin2dec(decoded_header[:18])
        user_nb = bin2dec(decoded_header[18:])

        return (cell_ident, user_nb)

    def decode_PBCH(self) -> tuple[int, int, list[dict[str, int]]]:
        '''
        Uses a method to retreive the PBCH from the matrix,
        then demods (2qam) it and decodes it (Hamming748).
        Retreives the cell ident and the number of users.

        Returns:
            tuple[int, int, list[dict]]: (cell_ident, user_nb, [{'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'harq': <harq>}, ...])
        '''

        #TODO: remove this useless method ?

        # Retreiving header data
        self.cell_ident, self.user_nb = self.decode_PBCH_header()

        user_data = []
        for user_idx in range(self.user_nb):
            user_data.append(self.extract_PBCH_user_data(user_idx))

        return self.cell_ident, self.user_nb, user_data

    def decode_PBCH_user(self, user_ident: int) -> dict[str, int]:
        '''
        Uses a method to retreive the PBCH from the matrix,
        then demods (2qam) it and decodes it (Hamming748).
        Retreives the cell ident and the number of users.
        Then it parses all the matrix to find the user `user_ident`.

        Args:
            :user_ident: the user identifier.

        Returns:
            dict[str, int]: {'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'harq': <harq>}
        '''

        # Retreiving header data
        self.cell_ident, self.user_nb = self.decode_PBCH_header()

        for user_idx in range(self.user_nb):
            if self.is_user_at_block(user_idx, user_ident):
                extracted_data = self.extract_PBCH_user_data(user_idx)
                return extracted_data

        raise ValueError(f'DecodeMatrix: decode_PBCH_user: user {user_ident} not found in the PBCH !')

    def extract_PBCH_user_data(self, user_idx: int) -> dict[str, int]:
        '''
        Extracts the data from a 24 bits PBCHU block.

        Args:
            :user_idx: the index of the user to extract data.

        Returns:
            dict[str, int]: {'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'harq': <harq>}
        '''

        if self.flattened_mat == None:
            raise ValueError('DecodeMatrix: extract_PBCH_user_data: self.flattened_mat not defined (run self.decode_PBCH first)')
    
        # Get the relevent part of the PBCH
        pbchu_k = demod_decode_block(self.flattened_mat[(user_idx + 1) * 48 : (user_idx + 2) * 48])

        ret = {}
        ret['user_ident'] = bin2dec(pbchu_k[:8]) # 8 bits for user ident
        ret['mcs'] = bin2dec(pbchu_k[8:10]) # 2 bits for MCS of PDCCHU
        ret['symb_start'] = bin2dec(pbchu_k[10:14]) # 4 bits for Symb start of PDCCHU
        ret['rb_start'] = bin2dec(pbchu_k[14:20]) # 6 bits for RB start of PDCCHU
        ret['harq'] = bin2dec(pbchu_k[20:]) # 4 bits for HARQ of PDCCHU

        return ret

    def is_user_at_block(self, user_idx: int, user_ident: int) -> bool:
        '''
        Extracts the user ident from the block at position `user_idx` and check if it is the same as `user_ident`.

        Args:
            :user_idx: the index of the user to extract data.
            :user_ident: the user identifier.

        Returns:
            bool: PBCHU_k['user_ident'] == user_ident
        '''

        if self.flattened_mat == None:
            raise ValueError('DecodeMatrix: is_user_at_block: self.flattened_mat not defined (run self.decode_PBCH first)')

        # Get the relevent part of the PBCH
        pbchu_k = demod_decode_block(self.flattened_mat[(user_idx + 1) * 48 : (user_idx + 2) * 48]) #TODO: does not work for index 7 ...

        user_ident_from_mat = bin2dec(pbchu_k[:8]) # 8 bits for user ident

        return user_ident == user_ident_from_mat

    def decode_PDCCHU_user(self, user_ident: int) -> dict[str, int]:
        '''
        Retreives the data from the PDCCHU concerning the user `user_ident` from the matrix using `self.decode_PBCH_user`.

        Args:
            :user_ident: the identifier of the user to retreive the data
        
        Returns:
            dict[str, int]: {'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'crc': <crc>}
        '''

        self.retreive_PBCH()
    
        user_data = self.decode_PBCH_user(user_ident)

        beg_index = flatten_index(user_data['symb_start'] - 3, (user_data['rb_start'] - 1) * 12)

        modulated_data = self.flattened_mat[
            beg_index : beg_index + 3 * 12
        ]

        decoded = demod_decode_block(modulated_data, user_data['mcs']) # 36 complex numbers -> 72 bits (4qam) -> 36 bits (Hamming748)

        ret = {}
        ret['user_ident'] = bin2dec(decoded[:8]) # 8 bits
        ret['mcs'] = bin2dec(decoded[8:14]) # 6 bits
        ret['symb_start'] = bin2dec(decoded[14:18]) # 4 bits
        ret['rb_start'] = bin2dec(decoded[18:24]) # 6 bits
        ret['rb_size'] = bin2dec(decoded[24:34]) # 10 bits
        ret['crc'] = bin2dec(decoded[34:36]) # 2 bits

        return ret


##-Tests
def test_decode_PBCH_user(user_ident=9):
    m1 = get_matrix('data/tfMatrix.csv')
    d = DecodeMatrix(m1)
    u = d.decode_PBCH_user(user_ident)
    print(u)

def test_decode_all_PBCH(matrix):
    '''Tests the `DecodeMatrix.decode_PBCH_user` method.'''

    d = DecodeMatrix(matrix)
    cell_ident, nb_users = d.decode_PBCH_header()

    print('\nPBCH decoded data :')
    print(f'    cell_ident: {cell_ident}')
    print(f'    nb_users: {nb_users}\n')

    for user_ident in range(1, nb_users + 1):
        user_data = d.decode_PBCH_user(user_ident)
        print(f'    {user_data}')

def test_decode_all_PDCCHU(matrix):
    '''Tests the `DecodeMatrix.decode_PDCCHU_user` method.'''

    d = DecodeMatrix(matrix)
    _, nb_users = d.decode_PBCH_header()

    print('\nPDCCHU decoded data :')

    for user_ident in range(1, nb_users + 1):
        data = d.decode_PDCCHU_user(user_ident)
        print('    ' + str(data))

