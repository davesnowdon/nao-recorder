'''
Created on 6 Jul 2013

@author: dns
'''
import unittest
import math
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

    def testArmsForward(self):
        
        # joint positions
        joint_dict = make_joint_dict(POSITION_ZERO)

        # call function
        result = fluentnao_translator.detect_command(joint_dict)

        # command
        command = result[0]
        self.assertEqual("arms.left_forward", command, "Should detect command arms forward")

        # pitch offset
        desired_pitch_offset = math.degrees(joint_dict['LShoulderPitch'])
        actual_pitch_offset = result[1][0]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = math.degrees(joint_dict['LShoulderRoll'])
        actual_roll_offset = result[1][1]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")





if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()