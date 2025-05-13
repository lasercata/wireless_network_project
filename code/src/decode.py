import numpy as np

from src.demod import bpsk_demod
from src.hamming748 import Hamming748
from src.utils import bin2dec

class DecodeMatrix:
    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix
        self.decoded_pbch = None

    def decode_PBCH(self) -> tuple[int, list[dict[str, int]]]:
        '''
        Uses a method to retreive the PBCH from the matrix,
        then demods (2qam) it and decodes it (Hamming748).
        Retreives the cell ident and the number of users.

        Returns:
            tuple[int, list[dict]]: (user_nb, [{'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'harq': <harq>}, ...])
        '''

        # Retreiving the PBCH from the matrix
        pbch = self.retreive_PBCH()

        # Demoding the PBCH to 2qam
        pbch_demoded = bpsk_demod(pbch)

        # Decoding with Hamming
        h = Hamming748()
        self.decoded_pbch = h.decode(pbch_demoded)

        # Retreiving cell ident (18 bits) and user number (6 bits)
        self.cell_ident, self.user_nb = self.extract_PBCH_header_data()

        user_data = []
        for user_idx in range(self.user_nb):
            user_data.append(self.extract_PBCH_user_data(user_idx))

        return self.user_nb, user_data

    def extract_PBCH_header_data(self) -> tuple[int, int]:
        '''
        Extracts cell ident and user number from the (decoded) PBCH 24 first bits.

        Args:
            pbch_decoded_header: the 24 first decoded bits of the PBCH.

        Returns:
            tuple: (cell ident, number of users).
        '''

        if self.decoded_pbch == None:
            raise ValueError('DecodeMatrix: extract_PBCH_header_data: self.decoded_pbch not defined (run self.decode_PBCH first)')

        # Get the relevent part of the PBCH
        pbch_decoded_header = self.decoded_pbch[:24] # the 24 first bits of the decoded PBCH correspond to cell ident (18 bits) and nb users (6 bits).
    
        # Retreiving cell ident (18 bits) and user number (6 bits)
        cell_ident = bin2dec(pbch_decoded_header[:18])
        user_nb = bin2dec(pbch_decoded_header[18:])

        return (cell_ident, user_nb)

    def extract_PBCH_user_data(self, user_idx: int) -> dict[str, int]:
        '''
        TODO: Docstring for extract_PBCH_user_data.

        Args:
            :user_idx: the index of the user to extract data.

        Returns:
            dict[str, int]: {'user_ident': <user_ident>, 'mcs': <mcs>, 'symb_start': <symb_start>, 'rb_start': <rb_start>, 'harq': <harq>}
        '''

        if self.decoded_pbch == None:
            raise ValueError('DecodeMatrix: extract_PBCH_user_data: self.decoded_pbch not defined (run self.decode_PBCH first)')
    
        # Get the relevent part of the PBCH
        pbchu_k = self.decoded_pbch[(user_idx + 1) * 24 : (user_idx + 2) * 24]

        user_ident = bin2dec(pbchu_k[:8]) # 8 bits for user ident
        mcs = bin2dec(pbchu_k[8:10]) # 2 bits for MCS of PDCCHU
        symb_start = bin2dec(pbchu_k[10:14]) # 4 bits for Symb start of PDCCHU
        rb_start = bin2dec(pbchu_k[14:20]) # 6 bits for RB start of PDCCHU
        harq = bin2dec(pbchu_k[20:]) # 4 bits for HARQ of PDCCHU

        # return (user_ident, mcs, symb_start, rb_start, harq)
        return {
            'user_ident': user_ident,
            'mcs': mcs,
            'symb_start': symb_start,
            'rb_start': rb_start,
            'harq': harq
        }


    def retreive_PBCH(self) -> np.ndarray:
        """retreives the PBCH (broadcast channel) from the matrix

        Returns:
            np.ndarray: the PBCH we retreived
        """

        pass

