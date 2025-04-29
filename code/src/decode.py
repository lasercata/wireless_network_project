import numpy as np

from src.demod import bpsk_demod
from src.hamming748 import Hamming748
from src.utils import bin2dec

class DecodeMatrix:
    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix

        def decode_PBCH(self) -> tuple:
            """uses a method to retreive the PBCH from the matrix,
            then demods (2qam) it and decodes it (Hamming748).
            Retreives the cell ident and the number of users.

            Returns:
                tuple: (cell ident, number of users).
            """

            # Retreiving the PBCH from the matrix
            pbch = self.retreive_PBCH()

            # Demoding the PBCH to 2qam
            pbch_demoded = bpsk_demod(pbch)

            # Decoding with Hamming
            h = Hamming748()
            pbch_decoded = h.decode(pbch_demoded) # pbch_decoded should be 24 bits long

            # Retreiving cell ident (18 bits) and user number (6 bits)
            cell_ident = bin2dec(pbch_decoded[:18])
            user_nb = bin2dec(pbch_decoded[18:])

            return (cell_ident, user_nb)


        def retreive_PBCH(self) -> np.ndarray:
            """retreives the PBCH (broadcast channel) from the matrix

            Returns:
                np.ndarray: the PBCH we retreived
            """

            pass

