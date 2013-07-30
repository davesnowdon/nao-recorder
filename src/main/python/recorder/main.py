'''
Created on 7 Jul 2013

@author: davesnowdon
'''

import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.extras.highlight import KivyLexer
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.lang import Builder

from pygments import lexers
from pygame import font as fonts
import codecs, os
import logging


from core import Robot, get_joints_for_chain, is_joint, get_sub_chains

WORD_RECOGNITION_MIN_CONFIDENCE = 0.6

main_logger = logging.getLogger("recorder.main")

class Fnt_SpinnerOption(SpinnerOption):
    pass


class LoadDialog(Popup):

    def load(self, path, selection):
        self.choosen_file = [None, ]
        self.choosen_file = selection
        Window.title = selection[0][selection[0].rfind(os.sep) + 1:]
        self.dismiss()

    def cancel(self):
        self.dismiss()


class SaveDialog(Popup):

    def save(self, path, selection):
        _file = codecs.open(selection, 'w', encoding='utf8')
        _file.write(self.text)
        Window.title = selection[selection.rfind(os.sep) + 1:]
        _file.close()
        self.dismiss()

    def cancel(self):
        self.dismiss()


class ConnectionDialog(Popup):
    pass

class NaoJoints(BoxLayout):
    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(NaoJoints, self).__init__(**kwargs)

        self.on_joint_selection = kwargs['on_joint_selection']

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
        return self.children[0].children

    def toggle_joint(self, btn, joint_name):
        # print "btn = {}, name = {} state = {}".format(btn, joint_name, btn.state)
        self.notify_joint_selection_changed()

    def child_joint_name(self, child):
        return child.text

    def is_selected(self, child):
        return isinstance(child, ToggleButton) and \
               is_joint(self.child_joint_name(child)) and \
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

class NaoRecorderApp(App):

    files = ListProperty([None, ])

    def build(self):
        self.robot = Robot(status_display=self, code_display=self)

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
            text='File',
            values=('Connect', 'Open', 'SaveAs', 'Save', 'Close'))
        mnu_file.bind(text=self._file_menu_selected)

        # motors on/off
        btn_motors_on = Button(text='Motors On')
        btn_motors_on.bind(on_press=self._on_motors_on)

        btn_motors_off = Button(text='Motors Off')
        btn_motors_off.bind(on_press=self._on_motors_off)

        # run script
        btn_run_script = Button(text='Run Script')
        btn_run_script.bind(on_press=self._on_run_script)

        # add keyframe
        btn_add_keyframe = Button(text='Add Keyframe')
        btn_add_keyframe.bind(on_press=self._on_add_keyframe)

        # root actions menu
        robot_actions = Spinner(
            text='Action',
            values=sorted(self.robot.postures()))
        robot_actions.bind(text=self.on_action)

        # add to menu
        menu.add_widget(mnu_file)
        menu.add_widget(btn_add_keyframe)
        menu.add_widget(btn_motors_on)
        menu.add_widget(btn_motors_off)
        menu.add_widget(btn_run_script)
        menu.add_widget(robot_actions)
        b.add_widget(menu)

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
        self.joints_ui = NaoJoints(size_hint=(0.4, 1), on_joint_selection=self._on_joint_selection)
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
        if value == 'Connect':
            self.show_connection_dialog(None)

        elif value == 'Open':
            if not hasattr(self, 'load_dialog'):
                self.load_dialog = LoadDialog()
            self.load_dialog.open()
            self.load_dialog.bind(choosen_file=self.setter('files'))
        elif value == 'SaveAs':
            if not hasattr(self, 'saveas_dialog'):
                self.saveas_dialog = SaveDialog()
            self.saveas_dialog.text = self.codeinput.text
            self.saveas_dialog.open()
        elif value == 'Save':
            if self.files[0]:
                _file = codecs.open(self.files[0], 'w', encoding='utf8')
                _file.write(self.codeinput.text)
                _file.close()
        elif value == 'Close':
            if self.files[0]:
                self.codeinput.text = ''
                Window.title = 'untitled'

    def on_files(self, instance, values):
        if not values[0]:
            return
        _file = codecs.open(values[0], 'r', encoding='utf8')
        self.codeinput.text = _file.read()
        _file.close()

    def on_action(self, instance, l):
        if self.robot.is_connected():
            self.robot.go_to_posture(l)


    def _on_motors_off(self, instance):
        self.robot.motors_off()

    def _on_motors_on(self, instance):
        self.robot.motors_on()

    def _on_run_script(self, instance):
        if self.robot.is_connected():
            # TODO: run only selected code
            # code = self.codeinput.selection_text
            # if not code or len(code) == 0:
            code = self.codeinput.text
            self.robot.run_script(code)

    def _on_add_keyframe(self, dummy1=None, dummy2=None, dummy=None):
        code = self.robot.keyframe()
        if code:
            self.append_code(code)

    def _on_joint_selection(self, enabled_joints):
        self.robot.set_enabled_joints(enabled_joints)

if __name__ == '__main__':
    NaoRecorderApp().run()
