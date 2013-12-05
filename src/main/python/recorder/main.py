'''
Created on 7 Jul 2013

@author: davesnowdon
'''

import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.extras.highlight import KivyLexer
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.lang import Builder

from pygments import lexers
from pygame import font as fonts
import codecs, os
import logging

from core import Robot, localized_text, get_joints_for_chain, is_joint, get_sub_chains, is_joint_chain, get_joint_chain_names, get_translator_names

WORD_RECOGNITION_MIN_CONFIDENCE = 0.6

main_logger = logging.getLogger("recorder.main")


class Fnt_SpinnerOption(SpinnerOption):
    pass


class LoadDialog(Popup):
    def localized_text(self, property_name):
        return localized_text(property_name)

    def load(self, path, selection):
        self.chosen_file = [None, ]
        self.chosen_file = selection
        Window.title = selection[0][selection[0].rfind(os.sep) + 1:]
        self.dismiss()

    def cancel(self):
        self.dismiss()


class SaveDialog(Popup):
    def localized_text(self, property_name):
        return localized_text(property_name)

    def save(self, path, selection):
        _file = codecs.open(selection, 'w', encoding='utf8')
        _file.write(self.text)
        Window.title = selection[selection.rfind(os.sep) + 1:]
        _file.close()
        self.dismiss()

    def cancel(self):
        self.dismiss()


class ConnectionDialog(Popup):
    def localized_text(self, property_name):
        return localized_text(property_name)


class ConfirmationDialog(Popup):
    def localized_text(self, property_name):
        return localized_text(property_name)
    def ok(self):
        self.is_ok = True
        self.dismiss()
    def cancel(self):
        self.is_ok = False
        self.dismiss()


class NaoJoints(BoxLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(NaoJoints, self).__init__(**kwargs)

        self.on_joint_selection = kwargs['on_joint_selection']
        self.on_chain_stiffness = kwargs['on_chain_stiffness']
        self.on_hand_open_close = kwargs['on_hand_open_close']

    def _make_child_dict(self):
        return {c.kvid : c for c in self.children[0].children if c.kvid}

    def make_child_dict(self):
        try:
            if not self.child_dict:
                self.child_dict = self._make_child_dict()
        except AttributeError:
            self.child_dict = self._make_child_dict()

    def find_child(self, kvid):
        '''
        Find a child element using the kvid property
        '''
        self.make_child_dict()
        try:
            return self.child_dict[kvid]
        except KeyError:
            return None

    def toggle_chain(self, btn, chain_name):
        # print "btn = {}, chain = {} state = {}".format(btn, chain_name, btn.state)
        joints = get_joints_for_chain(chain_name)
        # print "joints = {}".format(joints)
        sub_chains = get_sub_chains(chain_name)
        # print "sub chains = {}".format(sub_chains)
        for child in self.get_joint_buttons():
            if self.child_joint_name(child) in joints or child.text in sub_chains:
                child.state = btn.state
        self.notify_joint_selection_changed()

    def get_joint_buttons(self):
        '''
            Joint buttons have non-empty text
        '''
        return [c for c in self.children[0].children if c.text]

    def get_chain_stiffness_buttons(self):
        return [self.find_child("{}Stiffness".format(n)) for n in get_joint_chain_names() if n != 'Body' ]

    def toggle_joint(self, btn, joint_name):
        # print "btn = {}, name = {} state = {}".format(btn, joint_name, btn.state)
        self.notify_joint_selection_changed()

    def set_chain_stiffness(self, stiff_chain_names):
        '''
            Called to update UI to show chain as stiff or relaxed
        '''
        print "Stiff chain names = {}\n".format(stiff_chain_names)
        # ignore 'Body' since we don't have a button for the whole robot
        for name in [n for n in get_joint_chain_names() if n != 'Body' ]:
            chain = self.find_child("{}Stiffness".format(name))
            if chain:
                chain.state = 'down' if name in stiff_chain_names else 'normal'

    def toggle_chain_stiffness(self, btn, chain_name):
        print "toggle_chain_stiffness = {}\n".format(chain_name)
        self.notify_stiffness_changed()

    def child_joint_name(self, child):
        return child.text

    def is_selected(self, child):
        return isinstance(child, ToggleButton) and \
               is_joint(self.child_joint_name(child)) and \
               child.state == 'down'

    def child_stiffness_chain_name(self, child):
        for name in [n for n in get_joint_chain_names() if n != 'Body' ]:
            chain = self.find_child("{}Stiffness".format(name))
            if child.kvid == chain.kvid:
                return name
        return None

    def is_stiff(self, child):
        return isinstance(child, ToggleButton) and \
               is_joint_chain(self.child_stiffness_chain_name(child)) and \
               child.state == 'down'

    def get_selected_joints(self):
        selected_joints = set()
        for child in self.get_joint_buttons():
            if self.is_selected(child):
                selected_joints.add(self.child_joint_name(child))
        return selected_joints

    def notify_joint_selection_changed(self):
        if self.on_joint_selection:
            self.on_joint_selection(self.get_selected_joints())

    def get_stiff_chains(self):
        stiff_chains = set()
        for child in self.get_chain_stiffness_buttons():
            if self.is_stiff(child):
                stiff_chains.add(self.child_stiffness_chain_name(child))
        print "stiff chains (from UI) = {}".format(stiff_chains)
        return stiff_chains

    def notify_stiffness_changed(self):
        if self.on_chain_stiffness:
            self.on_chain_stiffness(self.get_stiff_chains())

    def toggle_hand(self, btn, hand_name):
        if self.on_hand_open_close:
            is_open = btn.state == 'down'
            self.on_hand_open_close(hand_name, is_open)


class NaoRecorderApp(App):

    files = ListProperty([None, ])

    def build(self):
        self.robot = Robot(status_display=self, code_display=self,
                           on_disconnect=self._on_disconnect,
                           on_stiffness=self._on_chain_stiffness_from_robot)

        # building Kivy Interface
        b = BoxLayout(orientation='vertical')

        menu = BoxLayout(
            size_hint_y=None,
            height='30pt')
        fnt_name = Spinner(
            text='DroidSansMono',
            option_cls=Fnt_SpinnerOption,
            values=sorted(map(str, fonts.get_fonts())))
        fnt_name.bind(text=self._update_font)

        # file menu
        mnu_file = Spinner(
            text=localized_text('file_menu_title'),
            values=(localized_text('file_connect'),
                    localized_text('file_open'),
                    localized_text('file_save_as'),
                    localized_text('file_save'),
                    localized_text('file_close')))
        mnu_file.bind(text=self._file_menu_selected)

        # motors on/off
        btn_motors = ToggleButton(text=localized_text('motors_on'),
                                  state='normal',
                                  background_down='stiff.png',
                                  background_normal='relaxed.png')
        btn_motors.bind(on_press=self._on_motors)
        self._motor_toggle_button = btn_motors

        btn_speech = ToggleButton(text=localized_text('speech_recognition'),
                                         state='down' if self.robot.is_speech_recognition_enabled else 'normal')
        btn_speech.bind(on_press=self._on_toggle_speech_recognition)

        btn_touch_sensors = ToggleButton(text=localized_text('touch_sensors'),
                                         state='down' if self.robot.is_touch_sensors_enabled else 'normal')
        btn_touch_sensors.bind(on_press=self._on_toggle_touch_sensors)

        # run script
        btn_run_script = Button(text=localized_text('run_script'))
        btn_run_script.bind(on_press=self._on_run_script)

        # root actions menu
        robot_actions = Spinner(
            text=localized_text('action_menu_title'),
            values=sorted(self.robot.postures()))
        robot_actions.bind(text=self.on_action)

        # add to menu
        menu.add_widget(mnu_file)
        menu.add_widget(btn_speech)
        menu.add_widget(btn_touch_sensors)
        menu.add_widget(btn_motors)
        menu.add_widget(btn_run_script)
        menu.add_widget(robot_actions)
        b.add_widget(menu)

        controls = BoxLayout(
            size_hint_y=None,
            height='30pt')

        # add keyframe
        btn_add_keyframe = Button(text=localized_text('add_keyframe'))
        btn_add_keyframe.bind(on_press=self._on_add_keyframe)
        controls.add_widget(btn_add_keyframe)

        # set read joint angles to enable animation to start from known position
        btn_update_joints = Button(text=localized_text('read_joints'))
        btn_update_joints.bind(on_press=self._on_read_joints)
        controls.add_widget(btn_update_joints)

        kf_duration_label = Label(text=localized_text('keyframe_duration_colon'))
        controls.add_widget(kf_duration_label)

        kf_duration_input = TextInput(text=str(self.robot.keyframe_duration), multiline=False)
        kf_duration_input.bind(text=self._on_keyframe_duration)
        controls.add_widget(kf_duration_input)

        # allow user to select which translator to use
        active_translator = Spinner(
            text=self.robot.get_translator_name(),
            values=get_translator_names())
        active_translator.bind(text=self._on_translator_changed)
        controls.add_widget(active_translator)
        self.active_translator = active_translator
        self.is_translator_cancel = False

        b.add_widget(controls)

        m = BoxLayout()
        code_status = BoxLayout(orientation='vertical', size_hint=(0.6, 1))

        # code input
        self.codeinput = CodeInput(
            lexer=lexers.PythonLexer(),
            font_name='data/fonts/DroidSansMono.ttf', font_size=12,
            text="nao.say('hi')")
        code_status.add_widget(self.codeinput)

        # status window
        self.status = TextInput(text="", readonly=True, multiline=True, size_hint=(1.0, 0.25))
        code_status.add_widget(self.status)


        m.add_widget(code_status)
        self.joints_ui = NaoJoints(size_hint=(0.4, 1),
                                   on_joint_selection=self._on_joint_selection,
                                   on_chain_stiffness=self._on_chain_stiffness,
                                   on_hand_open_close=self._on_hand_open_close)
        m.add_widget(self.joints_ui)

        b.add_widget(m)
        return b

    def on_start(self):
        self.show_connection_dialog(None)

    def on_stop(self):
        self.robot.disconnect()

    def get_code(self):
        return self.codeinput.text

    def set_code(self, code):
        self.codeinput.text = code

    def append_code(self, code):
        self.set_code("{}\r\n{}".format(self.get_code(), code))

    def add_status(self, text):
        self.status.text = self.status.text + "\n" + text

    def show_connection_dialog(self, b):
        p = ConnectionDialog()
        p.bind(on_dismiss=self.do_connect)
        p.open()

    def do_connect(self, popup):
        hostname = popup.f_hostname.text
        portnumber = int(popup.f_port.text)
        print "connect to = {}:{}".format(hostname, portnumber)

        main_logger.info("Connecting to robot at {host}:{port}".format(host=hostname, port=portnumber))
        if self.robot.connect(hostname, portnumber):
            self.add_status("Connected to robot at {host}:{port}".format(host=hostname, port=portnumber))
        else:
            self.add_status("Error connecting to robot at {host}:{port}".format(host=hostname, port=portnumber))
            self.show_connection_dialog(None)

    def _update_size(self, instance, size):
        self.codeinput.font_size = float(size)

    def _update_font(self, instance, fnt_name):
        instance.font_name = self.codeinput.font_name = \
            fonts.match_font(fnt_name)

    def _file_menu_selected(self, instance, value):
        if value == 'File':
            return
        instance.text = 'File'
        if value == localized_text('file_connect'):
            self.show_connection_dialog(None)

        elif value == localized_text('file_open'):
            if not hasattr(self, 'load_dialog'):
                self.load_dialog = LoadDialog()
            self.load_dialog.open()
            self.load_dialog.bind(chosen_file=self.setter('files'))
        elif value == localized_text('file_save_as'):
            if not hasattr(self, 'saveas_dialog'):
                self.saveas_dialog = SaveDialog()
            self.saveas_dialog.text = self.codeinput.text
            self.saveas_dialog.open()
        elif value == localized_text('file_save'):
            if self.files[0]:
                _file = codecs.open(self.files[0], 'w', encoding='utf8')
                _file.write(self.codeinput.text)
                _file.close()
        elif value == localized_text('file_close'):
            if self.files[0]:
                self.codeinput.text = ''
                Window.title = 'untitled'

    def on_files(self, instance, values):
        if not values[0]:
            return
        _file = codecs.open(values[0], 'r', encoding='utf8')
        self.codeinput.text = _file.read()
        _file.close()

    def _on_disconnect(self):
        self.show_connection_dialog(None)

    def on_action(self, instance, l):
        if self.robot.is_connected():
            self.robot.go_to_posture(l)

    def _on_translator_changed(self, instance, translator_name):
        if self.is_translator_cancel:
            self.is_translator_cancel = False
        else:
            if self.get_code().strip():
                if self.robot.can_convert_code():
                    msg = localized_text('translator_change_warning').format(src=self.robot.get_translator_name(), dest=translator_name)
                else:
                    msg = localized_text('translator_change_no_convert').format(src=self.robot.get_translator_name(), dest=translator_name)
                p = ConfirmationDialog()
                p.f_content.text = msg
                p.translator_name = translator_name
                p.bind(on_dismiss=self._on_translator_confirm_dismissed)
                p.open()
            else:
                # if code window is empty, no reason to warn
                self.robot.change_translator(translator_name, '')

    def _on_translator_confirm_dismissed(self, popup):
        if popup.is_ok:
            self.is_translator_cancel = False
            self.set_code(self.robot.change_translator(popup.translator_name, self.get_code()))
        else:
            # we need this as our callback will get called when we revert the value
            self.is_translator_cancel = True
            self.active_translator.text = self.robot.get_translator_name()

    def _on_motors(self, motor_button):
        if motor_button.state == 'down':
            motor_button.text = localized_text('motors_off')
            self.robot.motors_on()
        else:
            motor_button.text = localized_text('motors_on')
            self.robot.motors_off()

    def _on_run_script(self, instance):
        if self.robot.is_connected():
            # TODO: run only selected code
            # code = self.codeinput.selection_text
            # if not code or len(code) == 0:
            self.robot.run_script(self.get_code())

    def _on_add_keyframe(self, dummy1=None, dummy2=None, dummy=None):
        code = self.robot.keyframe()
        if code:
            self.append_code(code)

    def _on_read_joints(self, instance):
        self.robot.update_joints()

    def _on_keyframe_duration(self, instance, value):
        try:
            kf_duration = float(instance.text)
            self.robot.keyframe_duration = kf_duration
            print "Keyframe duration set to {}".format(kf_duration)
        except ValueError:
            self.robot.keyframe_duration = 1.0

    def _on_toggle_speech_recognition(self, instance):
        self.robot.enable_speech_recognition(instance.state == 'down')
        print "Speech recognition enabled = {}".format(self.robot.is_speech_recognition_enabled)

    def _on_toggle_touch_sensors(self, instance):
        self.robot.enable_touch_sensors(instance.state == 'down')
        print "Touch sensors enabled = {}".format(self.robot.is_touch_sensors_enabled)

    def _on_joint_selection(self, enabled_joints):
        self.robot.set_enabled_joints(enabled_joints)

    # callback from NAO joints when button changes
    def _on_chain_stiffness(self, chain_names):
        self._motor_toggle_button.state = 'down' if chain_names else 'normal'
        self.robot.set_chains_with_motors_on(chain_names)

    # callback from Robot when stiffness changes
    def _on_chain_stiffness_from_robot(self, stiff_chains):
        self.joints_ui.set_chain_stiffness(stiff_chains)

    def _on_hand_open_close(self, hand_name, is_open):
        '''
        Callback from NAO joints when hand buttons change state
        '''
        self.robot.hand_open(hand_name, is_open)

if __name__ == '__main__':
    NaoRecorderApp().run()
