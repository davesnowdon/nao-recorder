'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import math
import logging
import collections

import naoutil.naoenv as naoenv
from naoutil.general import find_class
from naoutil import broker
from naoutil import memory
import fluentnao.nao as nao

from mathutil import FLOAT_CMP_ACCURACY, feq

Joint = collections.namedtuple('Joint',
                               ['name', 'position', 'is_changed', 'delta'])

WORD_RECOGNITION_MIN_CONFIDENCE = 0.55

DEFAULT_TRANSLATOR_NAME = "translators.fluentnao.core.FluentNaoTranslator"
default_translator = None

# joint names in same order as returned by ALMotion.getAngles('Body')
JOINT_NAMES = ('HeadYaw', 'HeadPitch',
               'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll',
               'LWristYaw', 'LHand',
               'LHipYawPitch', 'LHipRoll', 'LHipPitch',
               'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
               'RHipYawPitch', 'RHipRoll', 'RHipPitch',
               'RKneePitch', 'RAnklePitch', 'RAnkleRoll',
               'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll',
               'RWristYaw', 'RHand')


def get_translator(name=None):
    global default_translator
    if not default_translator:
        default_translator = find_class(DEFAULT_TRANSLATOR_NAME)
    return default_translator()


def joints_to_degrees(joints, round_values=True):
    djoints = {}
    if round_values:
        for j, v in joints.iteritems():
            djoints[j] = round(math.degrees(v))
    else:
        for j, v in joints.iteritems():
            djoints[j] = math.degrees(v)
    return djoints


def joint_changes(oldangles, newangles, threshold=FLOAT_CMP_ACCURACY):
    """
    Return a dict mapping joint names to tuples containin the current value and whether
    the joint has changed.
    """
    deltas = {}
    for k in oldangles:
        j1 = oldangles[k]
        j2 = newangles[k]
        if not feq(j1, j2):
            deltas[k] = Joint(k, j2, True, j2 - j1)
        else:
            deltas[k] = Joint(k, j2, False, None)
    return deltas


class Robot(object):
    def __init__(self, status_display=None, code_display=None):
        super(Robot, self).__init__()
        self.status_display = status_display
        self.code_display = code_display
        self.broker = None
        self.nao = None
        self._motors_on = False
        self.logger = logging.getLogger("recorder.core.Robot")

        self.joints = { }
        for j in JOINT_NAMES:
            self.joints[j] = 0

        # using "now" instead of "nao" for better recognition
        self.vocabulary = {'left arm stiff': self._left_arm_stiff,
                           'left arm relax': self._left_arm_relax,
                           'right arm stiff': self._right_arm_stiff,
                           'right arm relax': self._right_arm_relax,
                           'left leg stiff': self._left_leg_stiff,
                           'left leg relax': self._left_leg_relax,
                           'right leg stiff': self._right_leg_stiff,
                           'right leg relax': self._right_leg_relax,
                           'head stiff': self._head_stiff,
                           'head relax': self._head_relax,
                           'now lie belly': self._lying_belly,
                           'now lie back': self._lying_back,
                           'now stand': self._stand,
                           'now crouch': self._crouch,
                           'now sit': self._sit,
                           'now key frame': self._add_keyframe
                           }

        self.standard_postures = {
                                  'stand_init': self._stand_init,
                                  'sit_relax': self._sit_relax,
                                  'stand_zero': self._stand_zero,
                                  'lying_belly': self._lying_belly,
                                  'lying_back': self._lying_back,
                                  'stand': self._stand,
                                  'crouch': self._crouch,
                                  'sit': self._sit
                                  }

        self.event_handlers = {
                               "HandLeftBackTouched": self._back_left_arm,
                               "HandRightBackTouched": self._back_right_arm,
                               "LeftBumperPressed": self._left_bumper,
                               "RightBumperPressed": self._right_bumper,
                               "FrontTactilTouched": self._head_front,
                               "RearTactilTouched": self._head_rear,
                               "ChestButtonPressed": lambda x, y, z: self._add_keyframe(),
                               "WordRecognized": self._word_recognised
                               }

    def connect(self, hostname, portnumber):
        self.broker = broker.Broker('NaoRecorder', naoIp=hostname, naoPort=portnumber)
        if self.broker:
            self.env = naoenv.make_environment(None)
            self.nao = nao.Nao(self.env, None)
            if self.event_handlers and self.vocabulary:
                self.env.speechRecognition.setWordListAsVocabulary(self.vocabulary.keys(), False)
            self.do_subscribe()
            return True
        else:
            return None

    def disconnect(self):
        if self.is_connected():
            self.do_unsubscribe()
            self.broker.shutdown()

    def do_subscribe(self):
        if self.event_handlers:
            for (key, value) in self.event_handlers.iteritems():
                memory.subscribeToEvent(key, value)

    def do_unsubscribe(self):
        if self.event_handlers:
            for key in self.event_handlers.keys():
                memory.unsubscribeToEvent(key)

    def safe_say(self, msg):
        """
        Gets NAO to say something but disables speech recognition while he says it
        """
        if self.is_connected():
            self.disable_speech_recognition()
            self.nao.say(msg)
            self.enable_speech_recognition()

    def enable_speech_recognition(self):
        if "WordRecognized" in self.event_handlers:
            memory.subscribeToEvent("WordRecognized", self.event_handlers["WordRecognized"])

    def disable_speech_recognition(self):
        if "WordRecognized" in self.event_handlers:
            memory.unsubscribeToEvent("WordRecognized")

    def is_connected(self):
        return self.broker

    def postures(self):
        return self.standard_postures.keys()

    def motors_on(self):
        if self.is_connected():
            self.status_display.add_status('Turning NAO motors on')
            self.nao.stiff()
            self._motors_on = True
            self.safe_say("Motors on")

    def motors_off(self):
        if self.is_connected():
            self.status_display.add_status('Turning NAO motors off')
            self.nao.relax()
            self._motors_on = False
            self.safe_say("Motors off")

    def get_joint_angles(self, use_radians=True):
        angles = self.env.motion.getAngles("Body", True)
        for n, v in zip(JOINT_NAMES, angles):
            self.joints[n] = v

        if use_radians:
            return self.joints
        else:
            return joints_to_degrees(self.joints, True)

    def get_joint(self, name):
        return self.joints[name]

    def keyframe(self):
        if self.is_connected():
            # get angles
            angles = self.get_joint_angles()
            print angles

            # translating
            translator = get_translator()
            commands = translator.detect_command(angles)
            command_str = translator.commands_to_text(commands, is_blocking=True, fluentnao="nao.")
            return command_str
        else:
            return None

    def run_script(self, code):
        if self.is_connected():
            self.disable_speech_recognition()
            self.nao.naoscript.run_script(code, '\n')
            self.enable_speech_recognition()

    def _word_recognised(self, dataName, value, message):
        print "word_recognised: {}".format(value)
        self.logger.debug("word_recognised: {}".format(value))
        word = value[0]
        confidence = value[1]
        if confidence > WORD_RECOGNITION_MIN_CONFIDENCE:
            self.status_display.add_status('Recognised: {}'.format(word))
            try:
                self.vocabulary[word]()
            except AttributeError:
                print "Could not find word {} in vocabulary".format(word)

    def _back_left_arm(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self._left_arm_relax()
            else:
                self._left_arm_stiff()

    def _back_right_arm(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self._right_arm_relax()
            else:
                self._right_arm_stiff()

    def _left_bumper(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self._left_leg_relax()
            else:
                self._left_leg_stiff()

    def _right_bumper(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self._right_leg_relax()
            else:
                self._right_leg_stiff()

    def _head_rear(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self._head_relax()
            else:
                self._head_stiff()

    def _head_front(self, dataName, value, message):
        if value == 1:
            self._add_keyframe()

    def _add_keyframe(self):
        code = self.keyframe()
        if code:
            self.code_display.append_code(code)

    def _left_arm_stiff(self):
        self.status_display.add_status("left arm stiff")
        self.nao.arms.left_stiff()
        self.safe_say("left arm stiff")

    def _left_arm_relax(self):
        self.status_display.add_status("left arm relaxed")
        self.nao.arms.left_relax()
        self.safe_say("left arm relaxed")

    def _right_arm_stiff(self):
        self.status_display.add_status("right arm stiff")
        self.nao.arms.right_stiff()
        self.safe_say("right arm stiff")

    def _right_arm_relax(self):
        self.status_display.add_status("right arm relaxed")
        self.nao.arms.right_relax()
        self.safe_say("right arm relaxed")

    def _left_leg_stiff(self):
        self.status_display.add_status("left leg stiff")
        self.nao.legs.left_stiff()
        self.safe_say("left leg stiff")

    def _left_leg_relax(self):
        self.status_display.add_status("left leg relaxed")
        self.nao.legs.left_relax()
        self.safe_say("left leg relaxed")

    def _right_leg_stiff(self):
        self.status_display.add_status("right leg stiff")
        self.nao.legs.right_stiff()
        self.safe_say("right leg stiff")

    def _right_leg_relax(self):
        self.status_display.add_status("right leg relaxed")
        self.nao.legs.right_relax()
        self.safe_say("right leg relaxed")

    def _head_stiff(self):
        self.status_display.add_status("head stiff")
        self.nao.head.stiff()
        self.safe_say("head stiff")

    def _head_relax(self):
        self.status_display.add_status("head relaxed")
        self.nao.head.relax()
        self.safe_say("head relaxed")

    # wrapper functions so we can create map of standard positions without robot connection
    def _stand_init(self):
        self.nao.stand_init()

    def _sit_relax(self):
        self.nao.sit_relax()

    def _stand_zero(self):
        self.nao.stand_zero()

    def _lying_belly(self):
        self.nao.lying_belly()

    def _lying_back(self):
        self.nao.lying_back()

    def _stand(self):
        self.nao.stand()

    def _crouch(self):
        self.nao.crouch()

    def _sit(self):
        self.nao.sit()
