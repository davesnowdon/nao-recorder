'''
Created on 4 Dec 2013

@author: davesnowdon
'''
import unittest
import json

from translators.json.core import JsonTranslator
from testutil import make_joint_dict, POSITION_ZERO, POSITION_ARMS_UP, POSITION_ARMS_OUT, POSITION_ARMS_DOWN, POSITION_ARMS_BACK, POSITION_ARMS_RIGHT_UP_LEFT_OUT, POSITION_ARMS_LEFT_UP_RIGHT_OUT, POSITION_ARMS_LEFT_FORWARD_RIGHT_DOWN, POSITION_ARMS_RIGHT_FORWARD_LEFT_DOWN, POSITION_ARMS_RIGHT_DOWN_LEFT_BACK, POSITION_ARMS_LEFT_DOWN_RIGHT_BACK, POSITION_HANDS_CLOSE, POSITION_HANDS_OPEN, POSITION_HANDS_RIGHT_OPEN_LEFT_CLOSE, POSITION_HANDS_LEFT_OPEN_RIGHT_CLOSE, POSITION_ELBOWS_STRAIGHT_TURN_IN, POSITION_ELBOWS_BENT_TURN_UP, POSITION_ELBOWS_STRAIGHT_TURN_DOWN, POSITION_WRISTS_CENTER, POSITION_WRISTS_TURN_IN, POSITION_WRISTS_TURN_OUT, POSITION_WRISTS_RIGHT_CENTER_LEFT_TURN_OUT, POSITION_WRISTS_RIGHT_TURN_IN_LEFT_CENTER, POSITION_HEAD_DOWN_HEAD_FORWARD, POSITION_HEAD_UP_HEAD_RIGHT, POSITION_HEAD_CENTER_HEAD_LEFT

def get_translator():
    return JsonTranslator()

class TestCommandsToText(unittest.TestCase):
    def testEmptyList(self):
        commands = []
        result = get_translator().commands_to_text(commands)
        # print "empty command result = {}".format(result)
        self.assertEqual("", result, "Empty commands should yield empty string")

    def testOneCommand(self):
        commands = [("HeadPitch", [0])]
        result = get_translator().commands_to_text(commands)
        # print "one command result = {}".format(result)

        result_obj = json.loads(result)
        self.assertEqual(0, result_obj["changes"]["HeadPitch"],
                         "HeadPitch joint should be in JSON")

    def testTwoCommands(self):
        commands = [("HeadPitch", [0]),
                    ("HeadYaw", [0])]
        result = get_translator().commands_to_text(commands)
        result_obj = json.loads(result)
        # print "two command result = {}".format(result)
        self.assertEqual(2, len(result_obj["changes"]),
                         "Two commands should yield 2 changed joint anbles")

    def testNoCommands(self):
        commands = []
        result = get_translator().commands_to_text(commands, is_blocking=True, fluentnao="nao.")
        self.assertEqual("", result, "empty command list should generate empty string")

    def testKeyframeWithDuration(self):
        commands = [("HeadPitch", [0]),
                    ("HeadYaw", [0])]
        result = get_translator().commands_to_text(commands, is_blocking=True,
                                                   keyframe_duration=1.0)
        result_obj = json.loads(result)
        # print "two command result = {}".format(result)
        self.assertEqual(1.0, result_obj["duration"], "Command should include duration")
        self.assertEqual(True, result_obj["is_blocking"], "Command should be blocking")

    def testNoCommandsithDuration(self):
        commands = []
        result = get_translator().commands_to_text(commands, is_blocking=True, fluentnao="nao.",
                                                   keyframe_duration=1.0)
        self.assertEqual("", result, "empty command list should generate empty string even with duration")
