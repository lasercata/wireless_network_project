#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##-Imports
from src.hamming748 import Hamming748
from tests.utils import *

##-Tests
hamming748_decode = lambda y: Hamming748().decode(y)

def test_hammingDecode():
    # Decoding when no errors leads to sequence recovering
    assert hamming748_decode([1, 1, 0, 1, 0, 0, 1, 0]) == [1, 1, 0, 1]
    assert hamming748_decode([1, 1, 0, 0, 1, 1, 0, 0]) == [1, 1, 0, 0]
    assert hamming748_decode([1, 1, 1, 1, 1, 1, 1, 1]) == [1, 1, 1, 1]
    assert hamming748_decode([0, 1, 1, 1, 1, 0, 0, 0]) == [0, 1, 1, 1]
    assert hamming748_decode([0, 1, 1, 0, 0, 1, 1, 0]) == [0, 1, 1, 0]
    assert hamming748_decode([0, 0, 1, 1, 0, 0, 1, 1]) == [0, 0, 1, 1]
    assert hamming748_decode([0, 0, 1, 0, 1, 1, 0, 1]) == [0, 0, 1, 0]
    assert hamming748_decode([0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1]) == [0, 0, 1, 1, 0, 0, 1, 0]

    # Ensure that one error is detected, and corrected
    assert hamming748_decode([1, 1, 0, 1, 0, 0, 0, 0]) == [1, 1, 0, 1]
    assert hamming748_decode([1, 1, 0, 0, 1, 1, 0, 0]) == [1, 1, 0, 0]
    assert hamming748_decode([1, 0, 1, 1, 1, 1, 1, 1]) == [1, 1, 1, 1]
    assert hamming748_decode([0, 1, 1, 1, 1, 0, 0, 0]) == [0, 1, 1, 1]
    assert hamming748_decode([0, 1, 1, 0, 0, 1, 1, 0]) == [0, 1, 1, 0]
    assert hamming748_decode([0, 0, 1, 1, 0, 0, 1, 0]) == [0, 0, 1, 1]
    assert hamming748_decode([0, 0, 1, 0, 1, 1, 0, 1]) == [0, 0, 1, 0]

    # Ensure that two errors cannot be corrected
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [1, 0, 1, 1, 0, 0, 1, 0])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [1, 1, 1, 1, 1, 1, 0, 0])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [0, 1, 1, 0, 1, 1, 1, 1])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [1, 0, 1, 1, 1, 0, 0, 0])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [1, 1, 1, 1, 0, 1, 1, 0])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [0, 1, 0, 1, 0, 0, 1, 1])
    assert test_error('hamming748_decode', ValueError, hamming748_decode, [0, 1, 0, 0, 1, 1, 0, 1])

    # assert hamming748_decode([1, 0, 1, 1, 0, 0, 1, 0]) != [1, 1, 0, 1]
    # assert hamming748_decode([1, 1, 1, 1, 1, 1, 0, 0]) != [1, 1, 0, 0]
    # assert hamming748_decode([0, 1, 1, 0, 1, 1, 1, 1]) != [1, 1, 1, 1]
    # assert hamming748_decode([1, 0, 1, 1, 1, 0, 0, 0]) != [0, 1, 1, 1]
    # assert hamming748_decode([1, 1, 1, 1, 0, 1, 1, 0]) != [0, 1, 1, 0]
    # assert hamming748_decode([0, 1, 0, 1, 0, 0, 1, 1]) != [0, 0, 1, 1]
    # assert hamming748_decode([0, 1, 0, 0, 1, 1, 0, 1]) != [0, 0, 1, 0]

if __name__ == '__main__':
    test_hammingDecode()
