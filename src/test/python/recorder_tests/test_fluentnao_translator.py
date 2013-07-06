'''
Created on 6 Jul 2013

@author: dns
'''
import unittest

import recorder.JointManager as JointManager
import translators.fluentnao.core as fluentnao_translator

POSITION_ZERO = [ -0.004643917083740234, 0.35584592819213867, 0.10120201110839844, 0.009161949157714844,
                  -0.21326804161071777, -0.03984212875366211, -0.009245872497558594, 0.974399983882904, 
                  -0.516916036605835, 0.27922987937927246, -1.5876480340957642, 1.236362099647522, 
                  0.9225810170173645, 4.1961669921875e-05, -0.516916036605835, -0.31136012077331543, 
                  -1.5923337936401367, 1.2502517700195312, 0.9235100746154785, 4.1961669921875e-05, 
                  0.07213997840881348, -0.013848066329956055, 0.45555615425109863, 0.04912996292114258, 
                  0.22545599937438965, 0.9771999716758728]

def make_joint_dict(angles):
    result = {}
    for n, v in zip(JointManager.JOINT_NAMES, angles):
        result[n] = v
    return result

class TestDetectArms(unittest.TestCase):

    def testName(self):
        joint_dict = make_joint_dict(POSITION_ZERO)
        self.assertEqual("arms.forward", fluentnao_translator.detect_command(joint_dict), 
                         "Should detect arms forward")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()