'''
Created on 6 Jul 2013

@author: dns
'''
import unittest

from translators.fluentnao.core import FluentNaoTranslator
from testutil import make_joint_dict, POSITION_ZERO, POSITION_ARMS_UP, POSITION_ARMS_OUT, POSITION_ARMS_DOWN, POSITION_ARMS_BACK, POSITION_ARMS_RIGHT_UP_LEFT_OUT, POSITION_ARMS_LEFT_UP_RIGHT_OUT, POSITION_ARMS_LEFT_FORWARD_RIGHT_DOWN, POSITION_ARMS_RIGHT_FORWARD_LEFT_DOWN, POSITION_ARMS_RIGHT_DOWN_LEFT_BACK, POSITION_ARMS_LEFT_DOWN_RIGHT_BACK, POSITION_HANDS_CLOSE, POSITION_HANDS_OPEN, POSITION_HANDS_RIGHT_OPEN_LEFT_CLOSE, POSITION_HANDS_LEFT_OPEN_RIGHT_CLOSE, POSITION_ELBOWS_STRAIGHT_TURN_IN, POSITION_ELBOWS_BENT_TURN_UP, POSITION_ELBOWS_STRAIGHT_TURN_DOWN, POSITION_WRISTS_CENTER, POSITION_WRISTS_TURN_IN, POSITION_WRISTS_TURN_OUT, POSITION_WRISTS_RIGHT_CENTER_LEFT_TURN_OUT, POSITION_WRISTS_RIGHT_TURN_IN_LEFT_CENTER, POSITION_HEAD_DOWN_HEAD_FORWARD, POSITION_HEAD_UP_HEAD_RIGHT, POSITION_HEAD_CENTER_HEAD_LEFT, POSITION_FEET_POINT_TOES, POSITION_FEET_RAISE_TOES, POSITION_FEET_TURN_OUT, POSITION_FEET_TURN_IN, POSITION_FEET_CENTER

def get_translator():
    return FluentNaoTranslator()

SHOULDER_JOINTS = set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll'])
ELBOW_JOINTS = set(['LElbowYaw', 'RElbowYaw', 'LElbowRoll', 'RElbowRoll'])
HAND_JOINTS = set(['LHand', 'RHand'])
WRIST_JOINTS = set(['LWristYaw', 'RWristYaw'])
HEAD_JOINTS = set(['HeadYaw', 'HeadPitch'])
FEET_JOINTS = set(['LAnkleRoll', 'LAnklePitch', 'RAnkleRoll', 'RAnklePitch'])

class TestCommandsToText(unittest.TestCase):
    def testEmptyList(self):
        commands = []
        result = get_translator().commands_to_text(commands)
        # print "empty command result = {}".format(result)
        self.assertEqual("", result, "Empty commands should yield empty string")

    def testOneCommand(self):
        commands = [("arms.forward", [0, 0, 0])]
        result = get_translator().commands_to_text(commands)
        # print "one command result = {}".format(result)
        self.assertEqual("arms.forward(0,0,0)", result,
                         "One command should yield command with parameters")

    def testTwoCommands(self):
        commands = [("arms.left_forward", [0, 0, 0]),
                    ("right_forward", [0, 0, 0])]
        result = get_translator().commands_to_text(commands)
        # print "two command result = {}".format(result)
        self.assertEqual("arms.left_forward(0,0,0).right_forward(0,0,0)", result,
                         "Two commands should yield command with parameters")

    def testNoCommands(self):
        commands = []
        result = get_translator().commands_to_text(commands, is_blocking=True, fluentnao="nao.")
        self.assertEqual("", result, "empty command list should generate empty string")

    def testKeyframeWithDuration(self):
        commands = [("arms.left_forward", [0, 0, 0]),
                    ("right_forward", [0, 0, 0])]
        result = get_translator().commands_to_text(commands, is_blocking=True, fluentnao="nao.",
                                                   keyframe_duration=1.0)
        # print "two command result = {}".format(result)
        self.assertEqual("nao.set_duration(1.0).arms.left_forward(0,0,0).right_forward(0,0,0).go()", result,
                         "Two command should yield commands with parameters and duration")

    def testNoCommandsithDuration(self):
        commands = []
        result = get_translator().commands_to_text(commands, is_blocking=True, fluentnao="nao.",
                                                   keyframe_duration=1.0)
        self.assertEqual("", result, "empty command list should generate empty string even with duration")

class TestCommandSelection(unittest.TestCase):
    def testOnlyUsesCommandsWithEnabledJoints(self):
        joint_dict = make_joint_dict(POSITION_ZERO)
        enabled_joints = set(['LShoulderPitch', 'LShoulderRoll'])
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, enabled_joints)
        command = result[0][0]
        self.assertEqual("arms.left_forward", command, "Should detect only left shoulder enalbed; instead got: {0}".format(result))

class TestDetectArms(unittest.TestCase):

    def testArmsForward(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ZERO)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with arms forward; instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("arms.forward", command, "Should detect command arms forward; instead got: {0}".format(result))


    def testArmsUp(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_UP)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with arms up; instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("arms.up", command, "Should detect command arms up; instead got: {0}".format(result))


    def testArmsOut(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_OUT)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with arms out; instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("arms.out", command, "Should detect command arms out; instead got: {0}".format(result))


    def testArmsDown(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_DOWN)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with arms down; instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("arms.down", command, "Should detect command arms down; instead got: {0}".format(result))


    def testArmsBack(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_BACK)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with arms back; instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("arms.back", command, "Should detect command arms back; instead got: {0}".format(result))


    def testArmsLeftUpRightOut(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_LEFT_UP_RIGHT_OUT)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include left_up and right_out; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_up" and  second_tuple[0] == "right_out") or (first_tuple[0] == "arms.right_out" and  second_tuple[0] == "left_up"):
            pass
        else:
            self.fail("expected arms.left_up.right_out or arms.right_out.left_up; instead got: {0}".format(result))


    def testArmsRightUpLeftOut(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_RIGHT_UP_LEFT_OUT)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_up and left_out; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.right_up" and  second_tuple[0] == "left_out") or (first_tuple[0] == "arms.left_out" and  second_tuple[0] == "right_up"):
            pass
        else:
            self.fail("expected arms.right_up.left_out or arms.left_out.right_up; instead got: {0}".format(result))

    def testArmsLeftForwardRightDown(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_LEFT_FORWARD_RIGHT_DOWN)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_down and left_forward; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_forward" and  second_tuple[0] == "right_down") or (first_tuple[0] == "arms.right_down" and  second_tuple[0] == "left_forward"):
            pass
        else:
            self.fail("expected arms.left_forward.right_down or arms.right_down.left_forward; instead got: {0}".format(result))

    def testArmsRightForwardLeftDown(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_RIGHT_FORWARD_LEFT_DOWN)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_forward and left_down; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.right_forward" and  second_tuple[0] == "left_down") or (first_tuple[0] == "arms.left_down" and  second_tuple[0] == "right_forward"):
            pass
        else:
            self.fail("expected arms.right_forward.left_down or arms.left_down.right_forward; instead got: {0}".format(result))

    def testArmsRightDownLeftBack(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_RIGHT_DOWN_LEFT_BACK)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include right_down and left_back; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_back" and  second_tuple[0] == "right_down") or (first_tuple[0] == "arms.right_down" and  second_tuple[0] == "left_back"):
            pass
        else:
            self.fail("expected arms.left_back.right_down or arms.right_down.left_back; instead got: {0}".format(result))

    def testArmsLeftDownRightBack(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ARMS_LEFT_DOWN_RIGHT_BACK)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 SHOULDER_JOINTS, SHOULDER_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with commands that include left_down and right_back; instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "arms.left_down" and  second_tuple[0] == "right_back") or (first_tuple[0] == "arms.right_back" and  second_tuple[0] == "left_down"):
            pass
        else:
            self.fail("expected arms.left_down.right_back or arms.right_back.left_down; instead got: {0}".format(result))

    def testHandsClose(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HANDS_CLOSE)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HAND_JOINTS, HAND_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with command hands.close(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("hands.close", command, "Should detect command hands close; instead got: {0}".format(result))


    def testHandsOpen(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HANDS_OPEN)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HAND_JOINTS, HAND_JOINTS)
        self.assertEqual(len(result), 1, "Should get one tuple with command hands.open(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("hands.open", command, "Should detect command hands open; instead got: {0}".format(result))

    def testHandsRightOpenLeftClose(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HANDS_RIGHT_OPEN_LEFT_CLOSE)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HAND_JOINTS, HAND_JOINTS)

        self.assertEqual(len(result), 2, "Should get two tuples with command hands.right_open().left_close(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "hands.right_open" and  second_tuple[0] == "left_close") or (first_tuple[0] == "hands.left_close" and  second_tuple[0] == "right_open"):
            pass
        else:
            self.fail("expected hands.right_open.left_close or hand.left_close.right_open; instead got: {0}".format(result))


    def testHandsLeftOpenRightClose(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HANDS_LEFT_OPEN_RIGHT_CLOSE)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HAND_JOINTS, HAND_JOINTS)

        self.assertEqual(len(result), 2, "Should get two tuples with command hands.left_open().right_close(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "hands.left_open" and  second_tuple[0] == "right_close") or (first_tuple[0] == "hands.right_close" and  second_tuple[0] == "left_open"):
            pass
        else:
            self.fail("expected arms.left_down.right_back or arms.right_back.left_down; instead got: {0}".format(result))

    def testElbowsStraightTurnIn(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ELBOWS_STRAIGHT_TURN_IN)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 ELBOW_JOINTS, ELBOW_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with command elbows.straight().turn_in(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "elbows.straight" and  second_tuple[0] == "turn_in") or (first_tuple[0] == "elbows.turn_in" and  second_tuple[0] == "straight"):
            pass
        else:
            self.fail("expected elbows.straight.turn_in or elbows.turn_in.straight; instead got: {0}".format(result))


    def testElbowsBentTurnUp(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ELBOWS_BENT_TURN_UP)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 ELBOW_JOINTS, ELBOW_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with command elbows.bent().turn_up(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "elbows.bent" and  second_tuple[0] == "turn_up") or (first_tuple[0] == "elbows.turn_up" and  second_tuple[0] == "bent"):
            pass
        else:
            self.fail("expected elbows.bent.turn_up or elbows.turn_up.bent; instead got: {0}".format(result))

    def testElbowsStraightTurnDown(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_ELBOWS_STRAIGHT_TURN_DOWN)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 ELBOW_JOINTS, ELBOW_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with command elbows.straight().turn_down(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "elbows.straight" and  second_tuple[0] == "turn_down") or (first_tuple[0] == "elbows.turn_down" and  second_tuple[0] == "straight"):
            pass
        else:
            self.fail("expected elbows.straight.turn_down or elbows.turn_down.straight; instead got: {0}".format(result))


    def testWristsCenter(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_WRISTS_CENTER)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 WRIST_JOINTS, WRIST_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command wrists.center(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("wrists.center", command, "Should detect command wrists center; instead go: {0}".format(result))


    def testWristsCenter(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_WRISTS_TURN_IN)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 WRIST_JOINTS, WRIST_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command wrists.turn_in(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("wrists.turn_in", command, "Should detect command wrists turn in; instead go: {0}".format(result))


    def testWristsCenter(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_WRISTS_TURN_OUT)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 WRIST_JOINTS, WRIST_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command wrists.turn_out(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("wrists.turn_out", command, "Should detect command wrists turn out; instead go: {0}".format(result))

    def testWristsRightCenterLeftTurnOut(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_WRISTS_RIGHT_CENTER_LEFT_TURN_OUT)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 WRIST_JOINTS, WRIST_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with command wrists.right_center().left_turn_out(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "wrists.right_center" and  second_tuple[0] == "left_turn_out") or (first_tuple[0] == "wrists.left_turn_out" and  second_tuple[0] == "right_center"):
            pass
        else:
            self.fail("expected wrists.right_center().left_turn_out() or wrists.left_turn_out().right_center(); instead got: {0}".format(result))


    def testWristsRightTurnInLeftCenter(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_WRISTS_RIGHT_TURN_IN_LEFT_CENTER)

        # call function under test

        result = get_translator().detect_command(joint_dict,
                                                 WRIST_JOINTS, WRIST_JOINTS)
        self.assertEqual(len(result), 2, "Should get two tuples with command wrists.right_turn_in().left_center(); instead got: {0}".format(result))

        # expect two tuples
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "wrists.right_turn_in" and  second_tuple[0] == "left_center") or (first_tuple[0] == "wrists.left_center" and  second_tuple[0] == "right_turn_in"):
            pass
        else:
            self.fail("expected wrists.right_turn_in().left_center() or wrists.left_center().right_turn_in(); instead got: {0}".format(result))


    def testHeadDownHeadForward(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HEAD_DOWN_HEAD_FORWARD)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HEAD_JOINTS, HEAD_JOINTS)
        self.assertEqual(len(result), 2, "Should get 2 tuple(s) ; instead got: {0}".format(len(result)))

        # expected tuple(s)
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "head.down" and  second_tuple[0] == "forward") or (first_tuple[0] == "head.forward" and  second_tuple[0] == "down"):
            pass
        else:
            self.fail("expected head.down().forward() or head.forward().down(); instead got: {0}".format(result))

    def testHeadUpHeadRight(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HEAD_UP_HEAD_RIGHT)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HEAD_JOINTS, HEAD_JOINTS)
        self.assertEqual(len(result), 2, "Should get 2 tuple(s) ; instead got: {0}".format(len(result)))

        # expected tuple(s)
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "head.up" and  second_tuple[0] == "right") or (first_tuple[0] == "head.right" and  second_tuple[0] == "up"):
            pass
        else:
            self.fail("expected head.up().right() or head.right().up(); instead got: {0}".format(result))

    def testHeadCenterHeadLeft(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_HEAD_CENTER_HEAD_LEFT)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 HEAD_JOINTS, HEAD_JOINTS)
        self.assertEqual(len(result), 2, "Should get 2 tuple(s) ; instead got: {0}".format(len(result)))

        # expected tuple(s)
        first_tuple = result[0]
        second_tuple = result[1]

        # command
        if (first_tuple[0] == "head.center" and  second_tuple[0] == "left") or (first_tuple[0] == "head.left" and  second_tuple[0] == "center"):
            pass
        else:
            self.fail("expected head.center().left() or head.left().center(); instead got: {0}".format(result))

    # , POSITION_FEET_TURN_OUT, POSITION_FEET_TURN_IN, 
    def testFeetCenter(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_FEET_CENTER)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 FEET_JOINTS, FEET_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command feet.center(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("feet.center", command, "Should detect command feet center; instead go: {0}".format(result))

    def testFeetPointToes(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_FEET_POINT_TOES)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 FEET_JOINTS, FEET_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command feet.point_toes(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("feet.point_toes", command, "Should detect command feet point toes; instead go: {0}".format(result))

    def testFeetRaiseToes(self):
        # joint positions
        joint_dict = make_joint_dict(POSITION_FEET_RAISE_TOES)

        # call function under test
        result = get_translator().detect_command(joint_dict,
                                                 FEET_JOINTS, FEET_JOINTS)

        self.assertEqual(len(result), 1, "Should get one tuple(s) with command feet.raise_toes(); instead got: {0}".format(result))

        # command
        command = result[0][0]
        self.assertEqual("feet.raise_toes", command, "Should detect command feet raise toes; instead go: {0}".format(result))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
