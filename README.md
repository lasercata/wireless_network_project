# Wireless Network project folder 

## Introduction
Welcome to the Wireless network GIT repository. You will find here all the stuff related to the project and in particular 
- The resources of the project (documentation)
- All CSV matrixes related to the received data 
Have fun !

## List of dependencies 
- pip3 install numpy
- pip3 install matplotlib 
- pip3 install pytest
- pip3 install scikit-dsp-comm

## Usage
```
$ python3 code/main.py

Usage: code/main.py matrix_filename [user_ident]
Or, to run the tests: code/main.py -t

Examples:
    To decode for user 3:    code/main.py data/tfMatrix.csv 3
    To decode for all users: code/main.py data/tfMatrix.csv
    To run all tests:        code/main.py -t
```
