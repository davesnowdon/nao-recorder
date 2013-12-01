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

SPEECH_RECOGNITION_KEY = "WordRecognized"

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

def get_joint_chain_names():
    return JOINT_CHAINS.keys()

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
    def __init__(self, status_display=None, code_display=None, on_disconnect=None, on_stiffness=None):
        super(Robot, self).__init__()
        self.status_display = status_display
        self.code_display = code_display
        self.on_disconnect = on_disconnect
        self.on_stiffness = on_stiffness
        self.broker = None
        self.nao = None
        self._motors_on = False
        self.logger = logging.getLogger("recorder.core.Robot")
        self.last_keyframe_joints = None
        self.keyframe_duration = 1.0
        self.is_speech_recognition_enabled = True

        self.joints = { }
        for j in JOINT_NAMES:
            self.joints[j] = 0

        # using "now" instead of "nao" for better recognition
        self.vocabulary = {'left arm stiff': self.left_arm_stiff,
                           'left arm relax': self.left_arm_relax,
                           'right arm stiff': self.right_arm_stiff,
                           'right arm relax': self.right_arm_relax,
                           'left leg stiff': self.left_leg_stiff,
                           'left leg relax': self.left_leg_relax,
                           'right leg stiff': self.right_leg_stiff,
                           'right leg relax': self.right_leg_relax,
                           'head stiff': self.head_stiff,
                           'head relax': self.head_relax,
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
                               SPEECH_RECOGNITION_KEY: self._word_recognised
                               }

        self.enabled_joints = set(JOINT_NAMES)
        self.left_arm_debounce = Debounce(self.left_arm_relax, self.left_arm_stiff)
        self.right_arm_debounce = Debounce(self.right_arm_relax, self.right_arm_stiff)

    def connect(self, hostname, portnumber):
        try:
            self.broker = broker.Broker('NaoRecorder', nao_id=hostname, nao_port=portnumber)
            if self.broker:
                self.env = naoenv.make_environment(None)
                self.nao = nao.Nao(self.env, None)
                try:
                    if self.event_handlers and self.vocabulary:
                        self.env.speechRecognition.setWordListAsVocabulary(self.vocabulary.keys(), False)
                except RuntimeError as e:
                    print "Error setting speech vocabulary: {}".format(e)
                self.do_subscribe()
                return True
            else:
                return None
        except IOError as e:
            return None
        except RuntimeError as e:
            return None

    def disconnect(self):
        if self.is_connected():
            self.do_unsubscribe()
            self.broker.shutdown()
            if self.on_disconnect:
                self.on_disconnect()

    def do_subscribe(self):
        if self.event_handlers:
            for (key, value) in self.event_handlers.iteritems():
                if key == SPEECH_RECOGNITION_KEY:
                    if self.is_speech_recognition_enabled:
                        memory.subscribe_to_event(key, value)
                else:
                    memory.subscribe_to_event(key, value)

    def do_unsubscribe(self):
        if self.event_handlers:
            for key in self.event_handlers.keys():
                memory.unsubscribe_to_event(key)

    def safe_say(self, msg):
        """
        Gets NAO to say something but disables speech recognition while he says it
        """
        if self.is_connected():
            self._disable_speech_recognition()
            self.nao.say_and_block(msg)
            if self.is_speech_recognition_enabled:
                self._enable_speech_recognition()

    def enable_speech_recognition(self, is_enabled):
        if self.is_speech_recognition_enabled != is_enabled:
            if is_enabled:
                self._enable_speech_recognition()
            else:
                self._disable_speech_recognition()
        self.is_speech_recognition_enabled = is_enabled
        print "Speech recognition is {}".format("enabled" if is_enabled else "disabled")
        return is_enabled

    def _enable_speech_recognition(self):
        if SPEECH_RECOGNITION_KEY in self.event_handlers:
            try:
                memory.subscribe_to_event(SPEECH_RECOGNITION_KEY, self.event_handlers[SPEECH_RECOGNITION_KEY])
            except RuntimeError as e:
                print "Error enabling speech recognition: {}".format(e)

    def _disable_speech_recognition(self):
        if SPEECH_RECOGNITION_KEY in self.event_handlers:
            try:
                memory.unsubscribe_to_event(SPEECH_RECOGNITION_KEY)
            except RuntimeError as e:
                print "Error disabling speech recognition: {}".format(e)

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
            self.notify_stiffness_changed()
            self.safe_say("Motors on")

    def motors_off(self):
        if self.is_connected():
            self.status_display.add_status('Turning NAO motors off')
            self.nao.relax()
            self._motors_on = False
            self.notify_stiffness_changed()
            self.safe_say("Motors off")

    def get_joint_angles(self, use_radians=True):
        angles = self.env.motion.getAngles("Body", True)
        for n, v in zip(JOINT_NAMES, angles):
            self.joints[n] = v

        if use_radians:
            return self.joints
        else:
            return joints_to_degrees(self.joints, True)

    def get_joint_stiffnesses(self):
        '''
            Get the stiffness values for individual joints
        '''
        return { n : v for n, v in zip(JOINT_NAMES, self.env.motion.getStiffnesses("Body")) }

    def get_stiff_chains(self, threshold=0.2):
        '''
            Get whether joint chains are stiff or not
        '''
        stiff_chains = set()
        joint_stiffnesses = self.get_joint_stiffnesses()
        print "joint stiffnesses = {}/n".format(joint_stiffnesses)
        chain_names = [n for n in JOINT_CHAINS.keys() if n != 'Body']
        for n in chain_names:
            stiff_joint_count = 0;
            for j in JOINT_CHAINS[n]:
                if joint_stiffnesses[j] > threshold:
                    stiff_joint_count = stiff_joint_count + 1
                if stiff_joint_count > 0:
                    stiff_chains.add(n)
        if len(stiff_chains) == len(chain_names):
            stiff_chains.add('Body')
        print "stiff chains = {}\n".format(stiff_chains)
        return stiff_chains

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
            command_str = translator.commands_to_text(commands, is_blocking=True, fluentnao="nao.",
                                                      keyframe_duration=self.keyframe_duration)
            self.last_keyframe_joints = angles.copy()
            return command_str
        else:
            return None

    def update_joints(self):
        '''
        Updates the current set of joint angles so that we can track changes from a known point
        '''
        if self.is_connected():
            self.last_keyframe_joints = self.get_joint_angles()

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

    def set_chains_with_motors_on(self, stiff_chain_names):
        '''
            Turn all the named motor chains on. Any chains not in the provided collection
            have their motors turned off
        '''
        chain_names = [n for n in JOINT_CHAINS.keys() if n != 'Body']

        name_map = {'Head': 'Head',
                    'Body': 'Body',
                    'LeftArm': 'LArm',
                    'RightArm': 'RArm',
                    'LeftLeg': 'LLeg',
                    'RightLeg': 'RLeg'}

        # ensure is a list not a set
        stiff_chains = [ name_map[n] for n in stiff_chain_names]
        print "set_chains_with_motors_on = {}".format(stiff_chains)

        relaxed_chains = [ name_map[n] for n in chain_names if n not in stiff_chain_names]
        print "set_chains_with_motors_off = {}".format(relaxed_chains)

        pStiffness = 1.0
        pRelaxed = 0.0
        pTimeLists = 0.5
        if stiff_chains:
            self.env.motion.stiffnessInterpolation(stiff_chains, pStiffness, pTimeLists)
        if relaxed_chains:
            self.env.motion.stiffnessInterpolation(relaxed_chains, pRelaxed, pTimeLists)

        if self._motors_on != bool(stiff_chains):
            self._motors_on = bool(stiff_chains)
            self.safe_say('Motors on' if self._motors_on else 'Motors off')

        # self.notify_stiffness_changed()

    def notify_stiffness_changed(self):
        if self.on_stiffness:
            self.on_stiffness(self.get_stiff_chains())

    def hand_open(self, hand_name, is_open):
        if hand_name == 'LHand':
            if is_open:
                self._left_hand_open()
            else:
                self._left_hand_close()

        if hand_name == 'RHand':
            if is_open:
                self._right_hand_open()
            else:
                self._right_hand_close()

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
                self.left_leg_relax()
            else:
                self.left_leg_stiff()

    def _right_bumper(self, dataName, value, message):
        if self._motors_on:
            if value == 1:
                self.right_leg_relax()
            else:
                self.right_leg_stiff()

    def _head_rear(self, dataName, value, message):
        print "head rear"
        if self._motors_on:
            if value == 1:
                self.head_relax()
            else:
                self.head_stiff()

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

    def _stiffness_change(self, msg, updateFunc):
        self.status_display.add_status(msg)
        self.safe_say(msg)
        updateFunc()
        self.notify_stiffness_changed()

    def left_arm_stiff(self):
        self._stiffness_change("left arm stiff", self._left_arm_stiff)

    def _left_arm_stiff(self):
        self.nao.arms.left_stiff()

    def left_arm_relax(self):
        self._stiffness_change("left arm relaxed", self._left_arm_relax)

    def _left_arm_relax(self):
        self.nao.arms.left_relax()

    def right_arm_stiff(self):
        self._stiffness_change("right arm stiff", self._right_arm_stiff)

    def _right_arm_stiff(self):
        self.nao.arms.right_stiff()

    def right_arm_relax(self):
        self._stiffness_change("right arm relaxed", self._right_arm_relax)

    def _right_arm_relax(self):
        self.nao.arms.right_relax()

    def left_leg_stiff(self):
        self._stiffness_change("left leg stiff", self._left_leg_stiff)

    def _left_leg_stiff(self):
        self.nao.legs.left_stiff()

    def left_leg_relax(self):
        self._stiffness_change("left leg relaxed", self._left_leg_relax)

    def _left_leg_relax(self):
        self.nao.legs.left_relax()

    def right_leg_stiff(self):
        self._stiffness_change("right leg stiff", self._right_leg_stiff)

    def _right_leg_stiff(self):
        self.nao.legs.right_stiff()

    def right_leg_relax(self):
        self._stiffness_change("right leg relaxed", self._right_leg_relax)

    def _right_leg_relax(self):
        self.nao.legs.right_relax()

    def head_stiff(self):
        self._stiffness_change("head stiff", self._head_stiff)

    def _head_stiff(self):
        self.nao.head.stiff()

    def head_relax(self):
        self._stiffness_change("head relaxed", self._head_relax)

    def _head_relax(self):
        self.nao.head.relax()

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
