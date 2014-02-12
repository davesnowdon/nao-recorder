'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import math
import logging
import locale
import os
import inspect

import naoutil.naoenv as naoenv
from naoutil.general import find_class
from naoutil import broker
from naoutil import memory
from naoutil import i18n
import fluentnao.nao as nao

from mathutil import FLOAT_CMP_ACCURACY, feq
from debounce import Debounce

WORD_RECOGNITION_MIN_CONFIDENCE = 0.55

TRANSLATORS = { 'FluentNAO' : "translators.fluentnao.core.FluentNaoTranslator",
                'JSON' : "translators.json.core.JsonTranslator",
                'Naojure' : 'translators.naojure.core.NaojureTranslator',
                'EDN' : 'translators.edn.core.EDNTranslator' }

DEFAULT_TRANSLATOR_NAME = 'FluentNAO'
translator_instances = {}

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

TOUCH_SENSOR_KEYS = [ "HandLeftBackTouched", "HandRightBackTouched", "LeftBumperPressed",
                      "RightBumperPressed", "FrontTactilTouched", "RearTactilTouched" ]

JOINT_MOVE_AMOUNT = math.pi / 180.0

core_logger = logging.getLogger("recorder.core")

def get_system_language_code():
    """
    Get the current language code or default to English (en)
    """
    (code, _) = locale.getlocale()
    if not code:
        (code, _) = locale.getdefaultlocale()
    if not code:
        code = 'en_GB'
    (lang, _) = code.split('_')
    return lang

language_code = get_system_language_code()

resource_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def localized_text(property_name):
    global resource_dir
    global language_code
    lt = i18n.get_property(resource_dir,
                            'naorecorder',
                            language_code,
                            property_name)
    core_logger.debug("Property '{name}' resolved to text '{value}' in language '{lang}'"
                      .format(name=property_name, value=lt, lang=language_code))
    return lt


def get_translator(name=None):
    global translator_instances
    if not name:
        name = DEFAULT_TRANSLATOR_NAME

    # force the name to be a valid translator
    try:
        clazzname = TRANSLATORS[name]
    except KeyError:
        name = DEFAULT_TRANSLATOR_NAME
        clazzname = TRANSLATORS[DEFAULT_TRANSLATOR_NAME]

    # get an existing translator instance or make a new one
    try:
        translator = translator_instances[name]
    except KeyError:
        klass = find_class(clazzname)
        translator = klass()
        translator_instances[name] = translator
    return translator

def get_translator_names():
    return TRANSLATORS.keys()

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
        self.is_touch_sensors_enabled = True
        self.translator = get_translator(DEFAULT_TRANSLATOR_NAME)

        self.joints = { }
        for j in JOINT_NAMES:
            self.joints[j] = 0

        # using "now" instead of "nao" for better recognition
        self.vocabulary = {localized_text("cmd_left_arm_stiff"): self.left_arm_stiff,
                           localized_text("cmd_left_arm_relax"): self.left_arm_relax,
                           localized_text("cmd_right_arm_stiff"): self.right_arm_stiff,
                           localized_text("cmd_right_arm_relax"): self.right_arm_relax,
                           localized_text("cmd_left_leg_stiff"): self.left_leg_stiff,
                           localized_text("cmd_left_leg_relax"): self.left_leg_relax,
                           localized_text("cmd_right_leg_stiff"): self.right_leg_stiff,
                           localized_text("cmd_right_leg_relax"): self.right_leg_relax,
                           localized_text("cmd_head_stiff"): self.head_stiff,
                           localized_text("cmd_head_relax"): self.head_relax,
                           localized_text("cmd_now_lie_belly"): self._lying_belly,
                           localized_text("cmd_now_lie_back"): self._lying_back,
                           localized_text("cmd_now_stand"): self._stand,
                           localized_text("cmd_now_crouch"): self._crouch,
                           localized_text("cmd_now_sit"): self._sit,
                           localized_text("cmd_now_key_frame"): self._add_keyframe,
                           localized_text("cmd_now_exit"): self._nao_exit,
                           localized_text("cmd_hello_now"): self._hello_nao,
                           localized_text("cmd_left_hand_open"): self._left_hand_open,
                           localized_text("cmd_left_hand_close"): self._left_hand_close,
                           localized_text("cmd_right_hand_open"): self._right_hand_open,
                           localized_text("cmd_right_hand_close"): self._right_hand_close
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

        self.event_handlers = { }
        if self.is_touch_sensors_enabled:
            self.event_handlers.update(self._touch_handler_dict())

        if self.is_speech_recognition_enabled:
            self.event_handlers.update(self._speech_handler_dict())

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
                        self.env.speechRecognition.setVocabulary(self.vocabulary.keys(), False)
                except RuntimeError as e:
                    print localized_text('error_set_vocabulary').format(e)
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

    def _enable_handlers(self, handlers):
        for key, handler in handlers.iteritems():
            try:
                memory.subscribe_to_event(key, handler)
            except RuntimeError as e:
                print localized_text('error_set_callback').format(e)
        self.event_handlers.update(handlers)

    def _disable_handlers(self, keys):
        for key in keys:
            if key in self.event_handlers:
                try:
                    memory.unsubscribe_to_event(key)
                    self.event_handlers.pop(key)
                except RuntimeError as e:
                    print localized_text('error_disable_callback').format(e)

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
                self.status_display.add_status(localized_text('status_enable_speech_recognition'))
                self._enable_speech_recognition()
            else:
                self.status_display.add_status(localized_text('status_disable_speech_recognition'))
                self._disable_speech_recognition()
        self.is_speech_recognition_enabled = is_enabled
        self.safe_say(localized_text('status_speech_recogniton_enabled' if is_enabled else 'status_speech_recogniton_disabled'))
        return is_enabled

    def _enable_speech_recognition(self):
        self._enable_handlers(self._speech_handler_dict())

    def _disable_speech_recognition(self):
        self._disable_handlers(self._speech_handler_dict().keys())

    def enable_touch_sensors(self, is_enabled):
        if self.is_touch_sensors_enabled != is_enabled:
            if is_enabled:
                self.status_display.add_status(localized_text('status_enable_touch_sensors'))
                self._enable_touch_sensors()
            else:
                self.status_display.add_status(localized_text('status_disable_touch_sensors'))
                self._disable_touch_sensors()
        self.is_touch_sensors_enabled = is_enabled
        self.safe_say(localized_text('status_touch_sensors_enabled' if is_enabled else 'status_touch_sensors_disabled'))
        return is_enabled

    def _enable_touch_sensors(self):
        self._enable_handlers(self._touch_handler_dict())

    def _disable_touch_sensors(self):
        self._disable_handlers(self._touch_handler_dict().keys())

    def _touch_handler_dict(self):
        return { "HandLeftBackTouched": self._back_left_arm,
                 "HandRightBackTouched": self._back_right_arm,
                 "LeftBumperPressed": self._left_bumper,
                 "RightBumperPressed": self._right_bumper,
                 "FrontTactilTouched": self._head_front,
                 "RearTactilTouched": self._head_rear }

    def _speech_handler_dict(self):
        return { SPEECH_RECOGNITION_KEY: self._word_recognised }

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
            self.status_display.add_status(localized_text('status_enable_motors'))
            self.nao.stiff()
            self._motors_on = True
            self.notify_stiffness_changed()
            self.safe_say(localized_text('status_motors_enabled'))

    def motors_off(self):
        if self.is_connected():
            self.status_display.add_status(localized_text('status_disable_motors'))
            self.nao.relax()
            self._motors_on = False
            self.notify_stiffness_changed()
            self.safe_say(localized_text('status_motors_disabled'))

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

    def get_translator_name(self):
        return self.translator.name

    def can_convert_code(self):
        return self.translator.is_reversible

    def is_code_runnable(self):
        return self.translator.is_runnable

    def change_translator(self, dest_name, existing_code):
        print "change translator = {}".format(dest_name)

        new_translator = get_translator(dest_name)

        converted_code = ''
        if self.can_convert_code():
            command_data = self.translator.parse(existing_code)
            converted_code = self.translate_data_to_code(new_translator, command_data)
            print "Changed existing code:\n{}\n to\n{}".format(existing_code, converted_code)

        self.translator = new_translator
        return converted_code

    def translate_data_to_code(self, translator, command_data):
        code_str = ''
        if command_data:
            angles = {}
            for cmd in command_data:
                print "cmd: {}".format(cmd)
                changed_angles = set(cmd['changes'].keys())
                angles.update(cmd['changes'])   # update the current state

                command_str = translator.generate(angles, changed_angles, changed_angles,
                                                  is_blocking=cmd['is_blocking'], fluentnao="nao.",
                                                  keyframe_duration=cmd['duration'])

                print "result: {}".format(command_str)
                code_str = translator.append(code_str, command_str)
        return code_str

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
            command_str = self.translator.generate(angles, changed_enabled_joints, self.enabled_joints,
                                                   is_blocking=True, fluentnao="nao.",
                                                   keyframe_duration=self.keyframe_duration)
            self.last_keyframe_joints = angles.copy()
            return command_str
        else:
            return None

    def append_command(self, code, new_command):
        return self.translator.append(code, new_command)

    def update_joints(self):
        '''
        Updates the current set of joint angles so that we can track changes from a known point
        '''
        if self.is_connected():
            self.last_keyframe_joints = self.get_joint_angles().copy()

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
            self.safe_say(localized_text('status_motors_enabled' if self._motors_on else 'status_motors_disabled'))

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
            self.status_display.add_status(localized_text('status_recognized_command').format(word))
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
        self.safe_say(localized_text('goodbye'))
        self.disconnect()

    def _hello_nao(self):
        self.safe_say(localized_text('hello'))

    def _left_hand_open(self):
        msg = localized_text("status_left_hand_open")
        self.status_display.add_status(msg)
        self.nao.hands.left_open()
        self.safe_say(msg)

    def _left_hand_close(self):
        msg = localized_text("status_left_hand_close")
        self.status_display.add_status(msg)
        self.nao.hands.left_close()
        self.safe_say(msg)

    def _right_hand_open(self):
        msg = localized_text("status_right_hand_open")
        self.status_display.add_status(msg)
        self.nao.hands.right_open()
        self.safe_say(msg)

    def _right_hand_close(self):
        msg = localized_text("status_right_hand_close")
        self.status_display.add_status(msg)
        self.nao.hands.right_close()
        self.safe_say(msg)

    def _stiffness_change(self, msg, updateFunc):
        l10n_msg = localized_text(msg)
        self.status_display.add_status(l10n_msg)
        self.safe_say(l10n_msg)
        updateFunc()
        self.notify_stiffness_changed()

    def left_arm_stiff(self):
        self._stiffness_change("status_left_arm_stiff", self._left_arm_stiff)

    def _left_arm_stiff(self):
        self.nao.arms.left_stiff()

    def left_arm_relax(self):
        self._stiffness_change("status_left_arm_relaxed", self._left_arm_relax)

    def _left_arm_relax(self):
        self.nao.arms.left_relax()

    def right_arm_stiff(self):
        self._stiffness_change("status_right_arm_stiff", self._right_arm_stiff)

    def _right_arm_stiff(self):
        self.nao.arms.right_stiff()

    def right_arm_relax(self):
        self._stiffness_change("status_right_arm_relaxed", self._right_arm_relax)

    def _right_arm_relax(self):
        self.nao.arms.right_relax()

    def left_leg_stiff(self):
        self._stiffness_change("status_left_leg_stiff", self._left_leg_stiff)

    def _left_leg_stiff(self):
        self.nao.legs.left_stiff()

    def left_leg_relax(self):
        self._stiffness_change("status_left_leg_relaxed", self._left_leg_relax)

    def _left_leg_relax(self):
        self.nao.legs.left_relax()

    def right_leg_stiff(self):
        self._stiffness_change("status_right_leg_stiff", self._right_leg_stiff)

    def _right_leg_stiff(self):
        self.nao.legs.right_stiff()

    def right_leg_relax(self):
        self._stiffness_change("status_right_leg_relaxed", self._right_leg_relax)

    def _right_leg_relax(self):
        self.nao.legs.right_relax()

    def head_stiff(self):
        self._stiffness_change("status_head_stiff", self._head_stiff)

    def _head_stiff(self):
        self.nao.head.stiff()

    def head_relax(self):
        self._stiffness_change("status_head_relaxed", self._head_relax)

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
