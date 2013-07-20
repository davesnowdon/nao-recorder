'''
Created on 6 Jul 2013

@author: dns
'''
import unittest
import math

from translators.fluentnao.core import FluentNaoTranslator
from testutil import POSITION_ZERO, POSITION_ARMS_UP, POSITION_ARMS_OUT, POSITION_ARMS_DOWN, POSITION_ARMS_LEFT_UP_RIGHT_OUT, POSITION_ARMS_LEFT_FORWARD_RIGHT_OUT, POSITION_ARMS_RIGHT_FORWARD_LEFT_OUT, make_joint_dict
from recorder.JointManager import joints_to_degrees

def get_translator():
    return FluentNaoTranslator()

class TestCommandsToText(unittest.TestCase):
    def testEmptyList(self):
        commands = []
        result = get_translator().commands_to_text(commands)
        print "empty command result = {}".format(result)
        self.assertEqual("", result, "Empty commands should yield empty string")

    def testOneCommand(self):
        commands = [("arms.forward", [0, 0, 0])]
        result = get_translator().commands_to_text(commands)
        print "one command result = {}".format(result)
        self.assertEqual("arms.forward(0,0,0)", result,
                         "One command should yield command with parameters")

    def testTwoCommands(self):
        commands = [("arms.left_forward", [0, 0, 0]),
                    ("right_forward", [0, 0, 0])]
        result = get_translator().commands_to_text(commands)
        print "two command result = {}".format(result)
        self.assertEqual("arms.left_forward(0,0,0).right_forward(0,0,0)", result,
                         "One command should yield command with parameters")

class TestDetectArms(unittest.TestCase):

    def testArmsForward(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ZERO)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple with arms forward")

        # expect one tuple
        first_tuple = result[0]

        # command
        command = first_tuple[0]
        self.assertEqual("arms.forward", command, "Should detect command arms forward")

        # pitch offset
        desired_pitch_offset = round(math.degrees(joint_dict['LShoulderPitch']))
        actual_pitch_offset = first_tuple[1][1]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = round(-math.degrees(joint_dict['LShoulderRoll']))
        actual_roll_offset = first_tuple[1][2]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")

    def testArmsUp(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_UP)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple with arms up")

        # expect one tuple
        first_tuple = result[0]

        # command
        command = first_tuple[0]
        self.assertEqual("arms.up", command, "Should detect command arms up")

        # pitch offset
        desired_pitch_offset = round(-90 - math.degrees(joint_dict['LShoulderPitch']))
        actual_pitch_offset = first_tuple[1][1]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = round(-math.degrees(joint_dict['LShoulderRoll']))
        actual_roll_offset = first_tuple[1][2]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")


    def testArmsOut(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_OUT)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple with arms out")

        # expect one tuple
        first_tuple = result[0]

        # command
        command = first_tuple[0]
        self.assertEqual("arms.out", command, "Should detect command arms out")

        # pitch offset
        desired_pitch_offset = round(-math.degrees(joint_dict['LShoulderPitch']))
        actual_pitch_offset = first_tuple[1][1]
        self.assertEqual(desired_pitch_offset, actual_pitch_offset, "Should match pitch offset")

        # roll offset
        desired_roll_offset = round(math.degrees(joint_dict['LShoulderRoll']) - 90)
        actual_roll_offset = first_tuple[1][2]
        self.assertEqual(desired_roll_offset, actual_roll_offset, "Should match roll offset")


    def testArmsDown(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_DOWN)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 1, "Should get one tuple with arms down")

        # expect one tuple
        first_tuple = result[0]

        # command
        command = first_tuple[0]
        self.assertEqual("arms.down", command, "Should detect command arms down")

    def testArmsLeftUpRightOut(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_LEFT_UP_RIGHT_OUT)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include left_up and right_out")

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_up" and  second_tuple[0] == "right_out") or (first_tuple[0] == "arms.right_out" and  second_tuple[0] == "left_up"):
            pass
        else:
            self.fail("expected arms.left_up.right_out or arms.right_out.left_up")

    def testArmsLeftForwardRightOut(self):

        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_LEFT_FORWARD_RIGHT_OUT)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_out and left_forward")

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_forward" and  second_tuple[0] == "right_out") or (first_tuple[0] == "arms.right_out" and  second_tuple[0] == "left_forward"):
            pass
        else:
            self.fail("expected arms.left_forward.right_out or arms.right_out.left_forward")

    def testArmsRightForwardLeftOut(self):
        
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_RIGHT_FORWARD_LEFT_OUT)

        # call function
        result = get_translator().detect_command(joint_dict)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_forward and left_out")

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.right_forward" and  second_tuple[0] == "left_out") or (first_tuple[0] == "arms.left_out" and  second_tuple[0] == "right_forward"):
            pass
        else:
            self.fail("expected arms.right_forward.left_out or arms.left_out.right_forward")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
