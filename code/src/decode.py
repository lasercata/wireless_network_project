#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##-Imports
import numpy as np
import sk_dsp_comm.fec_conv as fec

from src.binary_transformation import bitToByte, cesarDecode, toASCII
from src.crc import crc_decode, get_crc_poly
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

    #---Demodulation
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

    #---Decoding
    h = Hamming748()
    decoded = h.decode(demoded)

    return decoded

def demod_decode_PDSCH_block(block: list[np.complex128], mcs: int) -> list[int]:
    '''
    Demodulates and decodes a PDSCH block according to the `mcs`.

    Args:
        :block: the complex block to demod and decode
        :mcs: an integer indicating which demodulation algorithm to use. Possible values:
            mcs % 5:
                0 for bpsk,
                1 for qpsk,
                2 for 16qam,
                3 for 64qam (not implemented),
                4 for 256qam (not implemented)
            mcs // 5:
                0 for 1/3,
                1 for 1/2 (implemented),
                2 for 2/3,
                3 for 3/4,
                4 for 1/3 Hamming124,
                5 for 1/2 Hamming748 (implemented),
                6 for 2/3 Hamming128,
                7 for 3/4 Hamming2416
    '''

    #---Demodulation
    if mcs % 5 == 0:
        demoded = bpsk_demod(block)
    elif mcs % 5 == 1:
        demoded = qpsk_demod(block)
    elif mcs % 5 == 2:
        demoded = qam16_demod(block)
    else:
        raise NotImplementedError('Not implemented in this project')

    #---Decoding
    if mcs // 5 == 1:
        cc1 = fec.FECConv(('1011011', '1111001'), 6) # Create a 1/2 convolutional code object (brave AI)
        arr = np.array(demoded).astype(int)
        decoded_ = cc1.viterbi_decoder(arr, 'hard')

        decoded = [int(k) for k in decoded_]

    elif mcs // 5 == 5:
        h = Hamming748()
        decoded = h.decode(demoded)

    else:
        raise NotImplementedError('Not implemented in this project')

    return decoded

def payload_to_str(payload: list[int], user_ident: int) -> str:
    '''Converts a data block into an ASCII string.'''

    msg = bitToByte(payload)
    clear_msg = cesarDecode(user_ident, msg)

    return toASCII(clear_msg)

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
        pbchu_k = demod_decode_block(self.flattened_mat[(user_idx + 1) * 48 : (user_idx + 2) * 48])

        user_ident_from_mat = bin2dec(pbchu_k[:8]) # 8 bits for user ident

        return user_ident == user_ident_from_mat

    def decode_PDCCHU_user(self, user_ident: int) -> dict[str, int]:
        '''
        Retreives the data from the PDCCHU concerning the user `user_ident` from the matrix using `self.decode_PBCH_user`.

        Args:
            :user_ident: the identifier of the user to retreive the data
        
        Returns:
            dict[str, int]: {'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'crc_flag': <crc_flag>}
        '''

        user_data = self.decode_PBCH_user(user_ident)

        beg_index = flatten_index(user_data['symb_start'] - 3, (user_data['rb_start'] - 1) * 12)

        #TODO: this is an ugly fix. The number of resource blocks used for a PDCCHU section is hardcoded to 3 if mcs is 2, or 6 otherwise (mcs is 0).
        if user_data['mcs'] == 2:
            nb_of_rb = 3
        else:
            nb_of_rb = 6

        modulated_data = self.flattened_mat[beg_index : beg_index + nb_of_rb * 12]

        decoded = demod_decode_block(modulated_data, user_data['mcs']) # 36 complex numbers -> 72 bits (4qam) -> 36 bits (Hamming748)

        ret = {}
        ret['user_ident'] = bin2dec(decoded[:8]) # 8 bits
        ret['mcs'] = bin2dec(decoded[8:14]) # 6 bits
        ret['symb_start'] = bin2dec(decoded[14:18]) # 4 bits
        ret['rb_start'] = bin2dec(decoded[18:24]) # 6 bits
        ret['rb_size'] = bin2dec(decoded[24:34]) # 10 bits
        ret['crc_flag'] = bin2dec(decoded[34:36]) # 2 bits

        return ret

    def get_payload_user(self, user_ident: int) -> list[int]:
        '''
        Retreives the data corresponding to the user `user_ident`.

        Args:
            :user_ident: the identifier of the user.
        '''
    
        #-Get the data
        user_PDCCHU_data = self.decode_PDCCHU_user(user_ident)

        beg_index = flatten_index(user_PDCCHU_data['symb_start'] - 3, (user_PDCCHU_data['rb_start'] - 1) * 12)
        end_index = beg_index + 12 * user_PDCCHU_data['rb_size']

        # if end_index >= len(self.flattened_mat):
        #     return

        modulated_data = self.flattened_mat[beg_index : end_index]

        decoded = demod_decode_PDSCH_block(modulated_data, user_PDCCHU_data['mcs'])

        #-Check the CRC
        crc_size = 8 * (user_PDCCHU_data['crc_flag'] + 1)
        poly = get_crc_poly(crc_size)

        if crc_decode(decoded, poly) == 0:
            raise ValueError('DecodeMatrix: get_payload_user: error with CRC decoding (incorrect)')

        return decoded


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

def test_decode_all_payloads(matrix):
    '''Tests the `DecodeMatrix.get_payload_user` method.'''

    d = DecodeMatrix(matrix)
    _, nb_users = d.decode_PBCH_header()

    print(f'\nNumber of users: {nb_users}')
    print('payload data :')

    for user_ident in range(1, nb_users + 1):
        try:
            payload = d.get_payload_user(user_ident)
            s_pay = ''.join(str(k) for k in payload)
            print(f'    User #{user_ident}: {s_pay}')
            print(payload_to_str(payload, user_ident))

        except ValueError as err:
            print(f'    User #{user_ident}: error: {err}')

