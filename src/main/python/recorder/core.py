'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import math
import logging

import naoutil.naoenv as naoenv
from naoutil.general import find_class
from naoutil import broker
from naoutil import memory
import fluentnao.nao as nao

from mathutil import FLOAT_CMP_ACCURACY, feq
from debounce import Debounce

WORD_RECOGNITION_MIN_CONFIDENCE = 0.55

DEFAULT_TRANSLATOR_NAME = "translators.fluentnao.core.FluentNaoTranslator"
default_translator = None

# joint names in same order as returned by ALMotion.getAngles('Body')
JOINT_NAMES = ['HeadYaw', 'HeadPitch',
               'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll',
               'LWristYaw', 'LHand',
               'LHipYawPitch', 'LHipRoll', 'LHipPitch',
               'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
               'RHipYawPitch', 'RHipRoll', 'RHipPitch',
               'RKneePitch', 'RAnklePitch', 'RAnkleRoll',
               'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll',
               'RWristYaw', 'RHand']

JOINT_CHAIN_BODY = JOINT_NAMES

JOINT_CHAIN_HEAD = ['HeadYaw', 'HeadPitch']

JOINT_CHAIN_LEFT_ARM = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll',
               'LWristYaw', 'LHand']

JOINT_CHAIN_LEFT_LEG = ['LHipYawPitch', 'LHipRoll', 'LHipPitch',
               'LKneePitch', 'LAnklePitch', 'LAnkleRoll']

JOINT_CHAIN_RIGHT_ARM = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll',
               'RWristYaw', 'RHand']

JOINT_CHAIN_RIGHT_LEG = ['RHipYawPitch', 'RHipRoll', 'RHipPitch',
               'RKneePitch', 'RAnklePitch', 'RAnkleRoll']

JOINT_CHAINS = {'Head': JOINT_CHAIN_HEAD,
                'Body': JOINT_CHAIN_BODY,
                'LeftArm': JOINT_CHAIN_LEFT_ARM,
                'RightArm': JOINT_CHAIN_RIGHT_ARM,
                'LeftLeg': JOINT_CHAIN_LEFT_LEG,
                'RightLeg': JOINT_CHAIN_RIGHT_LEG}

JOINT_SUB_CHAINS = {'Head': [],
                    'Body': ['Head', 'LeftArm', 'RightArm', 'LeftLeg', 'RightLeg'],
                    'LeftArm': [],
                    'RightArm': [],
                    'LeftLeg': [],
                    'RightLeg': []
                    }

JOINT_MOVE_AMOUNT = math.pi / 180.0

def get_translator(name=None):
    global default_translator
    if not default_translator:
        default_translator = find_class(DEFAULT_TRANSLATOR_NAME)
    return default_translator()

def is_joint(name):
    global JOINT_NAMES
    return name in JOINT_NAMES

def is_joint_chain(name):
    global JOINT_CHAINS
    return name in JOINT_CHAINS.keys()

def get_sub_chains(name):
    global JOINT_SUB_CHAINS
    try:
        return JOINT_SUB_CHAINS[name]
    except AttributeError:
        return []

def get_joints_for_chain(name):
    '''
    Return the list of joints for a chain. If there is no chain of that name check whether it's a valid
    joint name and return that, otherwise None
    '''
    global JOINT_CHAINS
    try:
        return JOINT_CHAINS[name]
    except AttributeError:
        global JOINT_NAMES
        if name in JOINT_NAMES:
            return [name]
        else:
            return None

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
    Return a set containing the names of joints that have changed.
    """
    changed_joints = set()
    if oldangles:
        for k in newangles.keys():
            j1 = oldangles[k]
            j2 = newangles[k]
            if not feq(j1, j2, threshold):
                changed_joints.add(k)
    else:
        changed_joints.update(newangles.keys())
    return changed_joints


class Robot(object):
    def __init__(self, status_display=None, code_display=None):
        super(Robot, self).__init__()
        self.status_display = status_display
        self.code_display = code_display
        self.broker = None
        self.nao = None
        self._motors_on = False
        self.logger = logging.getLogger("recorder.core.Robot")
        self.last_keyframe_joints = None

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
                           'now key frame': self._add_keyframe,
                           'now exit': self._nao_exit,
                           'hello now': self._hello_nao,
                           'left hand open': self._left_hand_open,
                           'left hand close': self._left_hand_close,
                           'right hand open': self._right_hand_open,
                           'right hand close': self._right_hand_close
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

        self.enabled_joints = set(JOINT_NAMES)
        self.left_arm_debounce = Debounce(self._left_arm_relax, self._left_arm_stiff)
        self.right_arm_debounce = Debounce(self._right_arm_relax, self._right_arm_stiff)

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
            self.nao.say_and_block(msg)
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

    def go_to_posture(self, name):
        self.do_unsubscribe()
        try:
            try:
                self.standard_postures[name]();
            except KeyError as e:
                print "Failed to find posture {} exception {}".format(name, e)
        finally:
            self.do_subscribe()

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
            # print angles

            changed_joints = joint_changes(self.last_keyframe_joints, angles, JOINT_MOVE_AMOUNT)
            # print "changed joints = {}".format(changed_joints)
            # print "enabled joints = {}".format(self.enabled_joints)
            changed_enabled_joints = self.enabled_joints & changed_joints
            print "enabled changed joints = {}".format(changed_enabled_joints)

            # translating
            translator = get_translator()
            commands = translator.detect_command(angles, changed_enabled_joints, self.enabled_joints)
            command_str = translator.commands_to_text(commands, is_blocking=True, fluentnao="nao.")
            self.last_keyframe_joints = angles.copy()
            return command_str
        else:
            return None

    def run_script(self, code):
        if self.is_connected():
            # we disable event handling while a script is running. This is to avoid speech recognition
            # processing anything the robot says and also to attempt to ignore spurious triggering
            # of the hand sensors (which can get triggered by the motors)
            self.do_unsubscribe()
            try:
                self.nao.naoscript.run_script(code, '\n')
            finally:
                self.do_subscribe()

    def set_enabled_joints(self, enabled_joints):
        self.enabled_joints = set(enabled_joints.copy())
        print "Enabled joints are now {}".format(self.enabled_joints)

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
            self.left_arm_debounce.trigger(dataName, value, message)

    def _back_right_arm(self, dataName, value, message):
        if self._motors_on:
            self.right_arm_debounce.trigger(dataName, value, message)

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

    def _nao_exit(self):
        self.safe_say("bye bye")
        self.disconnect()

    def _hello_nao(self):
        self.safe_say("hello")

    def _left_hand_open(self):
        msg = "left hand open"
        self.status_display.add_status(msg)
        self.nao.hands.left_open()
        self.safe_say(msg)

    def _left_hand_close(self):
        msg = "left hand close"
        self.status_display.add_status(msg)
        self.nao.hands.left_close()
        self.safe_say(msg)

    def _right_hand_open(self):
        msg = "right hand open"
        self.status_display.add_status(msg)
        self.nao.hands.right_open()
        self.safe_say(msg)

    def _right_hand_close(self):
        msg = "right hand close"
        self.status_display.add_status(msg)
        self.nao.hands.right_close()
        self.safe_say(msg)

    def _left_arm_stiff(self):
        msg = "left arm stiff"
        self.status_display.add_status(msg)
        self.nao.arms.left_stiff()
        self.safe_say(msg)

    def _left_arm_relax(self):
        msg = "left arm relaxed"
        self.status_display.add_status(msg)
        self.nao.arms.left_relax()
        self.safe_say(msg)

    def _right_arm_stiff(self):
        msg = "right arm stiff"
        self.status_display.add_status(msg)
        self.nao.arms.right_stiff()
        self.safe_say(msg)

    def _right_arm_relax(self):
        msg = "right arm relaxed"
        self.status_display.add_status(msg)
        self.nao.arms.right_relax()
        self.safe_say(msg)

    def _left_leg_stiff(self):
        msg = "left leg stiff"
        self.status_display.add_status(msg)
        self.nao.legs.left_stiff()
        self.safe_say(msg)

    def _left_leg_relax(self):
        msg = "left leg relaxed"
        self.status_display.add_status(msg)
        self.nao.legs.left_relax()
        self.safe_say(msg)

    def _right_leg_stiff(self):
        msg = "right leg stiff"
        self.status_display.add_status(msg)
        self.nao.legs.right_stiff()
        self.safe_say(msg)

    def _right_leg_relax(self):
        msg = "right leg relaxed"
        self.status_display.add_status(msg)
        self.nao.legs.right_relax()
        self.safe_say(msg)

    def _head_stiff(self):
        msg = "head stiff"
        self.status_display.add_status(msg)
        self.nao.head.stiff()
        self.safe_say(msg)

    def _head_relax(self):
        msg = "head relaxed"
        self.status_display.add_status(msg)
        self.nao.head.relax()
        self.safe_say(msg)

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
