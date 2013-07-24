'''
Created on Jan 19, 2013

@author: dsnowdon
'''

import math

FLOAT_CMP_ACCURACY = 0.00000001

def feq(a, b, epsilon=FLOAT_CMP_ACCURACY):
    return abs(a - b) < epsilon

def is_zero(a, epsilon=FLOAT_CMP_ACCURACY):
    return abs(a) < epsilon
