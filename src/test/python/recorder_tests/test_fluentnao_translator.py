'''
Created on 6 Jul 2013

@author: dns
'''
import unittest
import math

from translators.fluentnao.core import FluentNaoTranslator
from testutil import POSITION_ZERO, POSITION_ARMS_UP, make_joint_dict


def get_translator():
    return FluentNaoTranslator()

class TestDetectArms(unittest.TestCase):

    def testArmsForward(self):
        
        # joint positions
        joint_dict = make_joint_dict(POSITION_ZERO)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple")

        # expect one tuple
        first_tuple = result[0]

        # command
        print 'first: ' + str(first_tuple)
        print 'cmd: {0}(0, {1},{2})'.format(first_tuple[0], first_tuple[1][0], first_tuple[1][1])
        command = first_tuple[0]
        self.assertEqual("arms.forward", command, "Should detect command arms forward")

        # pitch offset
        desired_pitch_offset = round(math.degrees(joint_dict['LShoulderPitch']))
        actual_pitch_offset = first_tuple[1][0]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = round(-math.degrees(joint_dict['LShoulderRoll']))
        actual_roll_offset = first_tuple[1][1]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")

    def testArmsUp(self):
        
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_UP)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple")

        # expect one tuple
        first_tuple = result[0]

        # command
        print 'first: ' + str(first_tuple)
        print 'cmd: {0}(0, {1},{2})'.format(first_tuple[0], first_tuple[1][0], first_tuple[1][1])
        command = first_tuple[0]
        self.assertEqual("arms.up", command, "Should detect command arms up")

        # pitch offset
        desired_pitch_offset = round(-90 - math.degrees(joint_dict['LShoulderPitch']))
        actual_pitch_offset = first_tuple[1][0]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = round(-math.degrees(joint_dict['LShoulderRoll']))
        actual_roll_offset = first_tuple[1][1]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()