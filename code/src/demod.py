import numpy as np
import math

def bpsk_demod(v: np.ndarray | list[np.complex128]) -> list[int]:
    """
    BPSK demodulation (2 QAM).
    The returned list is of the same length than the input one.

    Args:
        v (np.ndarray): input sequence.

    Returns:
        list[int]: calculated demodulation.
    """

    ret = []
    
    for c in v:
        if c.real <= 0:
            ret.append(0)
        else:
            ret.append(1)

    return ret

def qpsk_demod(v: np.ndarray | list[np.complex128]) -> list[int]:
    """
    QPSK demodulation.
    The length of the returned list is the twice the length of the input one.

    Args:
        v (np.ndarray): input sequence.

    Returns:
        list[int]: calculated demodulation.
    """

    ret = []

    for c in v:
        if c.real <= 0:
            ret.append(0)
        else:
            ret.append(1)

        if c.imag <= 0:
            ret.append(0)
        else:
            ret.append(1)

    return ret

def qam16_demod(v: np.ndarray | list[np.complex128]) -> list[int]:
    """qam16 demodulation.

    Args:
        v (np.ndarray): input sequence.

    Returns:
        list[int]: calculated demodulation.
    """

    if type(v) == list:
        v = np.array(v)

    # %FIXME Scaling vector 
    v = v * math.sqrt(2/3*(16-1))
    # Need to switch to vector 
    v = np.matrix.flatten(v)
    # Instantiate an empty list
    output_sequence = []
    # Decoding each element 
    for elem in v:
        # --- Real part decision 
        if np.real(elem) < -  2:
            bit1 = 1
            bit3 = 0
        elif  np.real(elem) < 0:
            bit1 = 1
            bit3 = 1
        elif  np.real(elem) < 2:
            bit1 = 0
            bit3 = 1
        else:
            bit1 = 0
            bit3 = 0

        # Imag part 
        if np.imag(elem) < -2:
            bit2 = 1
            bit4 = 0
        elif  np.imag(elem) < 0:
            bit2 = 1
            bit4 = 1
        elif  np.imag(elem) < 2:
            bit2 = 0
            bit4 = 1
        else:
            bit2 = 0
            bit4 = 0
        output_sequence.append(bit1)
        output_sequence.append(bit2)
        output_sequence.append(bit3)
        output_sequence.append(bit4)
    return output_sequence
