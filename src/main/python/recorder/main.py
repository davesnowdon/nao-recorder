'''
Created on 7 Jul 2013

@author: davesnowdon
'''

import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.extras.highlight import KivyLexer
from kivy.uix.button import Button
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


from core import get_translator, robot_connect, robot_disconnect


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


Builder.load_string('''
<ConnectionDialog>:
    size_hint: .5, .5
    auto_dismiss: False
    title: 'Connect to NAO'
    f_hostname: hostname
    f_port: port
    GridLayout:
        rows: 3
        cols: 2
        padding: 10
        spacing: 10
        Label:
            text: 'Address'
        TextInput:
            id: hostname
            text: 'nao.local'
        Label:
            text: 'Port number'
        TextInput:
            id: port
            text: '9559'
        Button:
            text: 'Connect'
            on_press: root.dismiss()

''')

class ConnectionDialog(Popup):
    pass


class NaoRecorderApp(App):

    files = ListProperty([None, ])

    def build(self):
        self.connection = None


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
                           'nao lie belly': self._lying_belly,
                           'nao lie back': self._lying_back,
                           'nao stand': self._stand,
                           'nao crouch': self._crouch,
                           'nao sit': self._sit
                           }

        # root actions menu
        self.standard_positions = {
                'stand_init': self._stand_init,
                'sit_relax': self._sit_relax,
                'stand_zero': self._stand_zero,
                'lying_belly': self._lying_belly,
                'lying_back': self._lying_back,
                'stand': self._stand,
                'crouch': self._crouch,
                'sit': self._sit
        }
        robot_actions = Spinner(
            text='Action',
            values=sorted(self.standard_positions.keys()))
        robot_actions.bind(text=self.on_action)

        # add to menu
        menu.add_widget(mnu_file)
        menu.add_widget(btn_add_keyframe)
        menu.add_widget(btn_motors_on)
        menu.add_widget(btn_motors_off)
        menu.add_widget(btn_run_script)
        menu.add_widget(robot_actions)
        b.add_widget(menu)

        # code input
        self.codeinput = CodeInput(
            lexer=lexers.PythonLexer(),
            font_name='data/fonts/DroidSansMono.ttf', font_size=12,
            text="nao.say('hi')")

        b.add_widget(self.codeinput)

        # status window
        self.status = TextInput(text="", readonly=True, multiline=True, size_hint=(1.0, 0.25))
        b.add_widget(self.status)

        return b

    def on_start(self):
        self.show_connection_dialog(None)

    def on_stop(self):
        if self.connection:
            robot_disconnect(self.connection)

    def add_status(self, text):
        self.status.text = self.status.text + "\n" + text

    def show_connection_dialog(self, b):
        p = ConnectionDialog()
        p.bind(on_dismiss=self.do_connect)
        p.open()

    def do_connect(self, popup):
        print "hostname = " + str(popup.f_hostname.text)
        print "port = " + str(popup.f_port.text)
        self._make_environment(popup.f_hostname.text, int(popup.f_port.text))

    def _make_environment(self, hostname, portnumber):
        main_logger.info("Connecting to robot at {host}:{port}".format(host=hostname, port=portnumber))

        event_handlers = {
                          "HandLeftBackTouched": self._back_left_arm,
                          "HandRightBackTouched": self._back_right_arm,
                          "LeftBumperPressed": self._left_bumper,
                          "RightBumperPressed": self._right_bumper,
                          "MiddleTactilTouched": self._head_middle,
                          "WordRecognized": self.word_recognised
                          }

        self.connection = robot_connect(hostname, portnumber, event_handlers, self.vocabulary.keys())
        if (self.connection):
            self.nao = self.connection.nao   # quick access to fluentniao
            self.add_status("Connected to robot at {host}:{port}".format(host=hostname, port=portnumber))
            self.motors_on = False

        else:
            self.add_status("Error connecting to robot at {host}:{port}".format(host=hostname, port=portnumber))
            self.show_connection_dialog(None)

    def word_recognised(self, dataName, value, message):
        word = value[0]
        confidence = value[1]
        if confidence > 0.7:
            self.add_status('Recognised: {}'.format(word))


    def _back_left_arm(self, dataName, value, message):
        if self.motors_on:
            if value == 1:
                self._left_arm_relax()
            else:
                self._left_arm_stiff()

    def _back_right_arm(self, dataName, value, message):
        if self.motors_on:
            if value == 1:
                self._right_arm_relax()
            else:
                self._right_arm_stiff()

    def _left_bumper(self, dataName, value, message):
        if self.motors_on:
            if value == 1:
                self._left_leg_relax()
            else:
                self._left_leg_stiff()

    def _right_bumper(self, dataName, value, message):
        if self.motors_on:
            if value == 1:
                self._right_leg_relax()
            else:
                self._right_leg_stiff()

    def _head_middle(self, dataName, value, message):
        if self.motors_on:
            if value == 1:
                self._head_relax()
            else:
                self._head_stiff()

    def _left_arm_stiff(self):
        self.add_status("left arm stiff")
        self.nao.arms.left_stiff()
        self.nao.say("left arm stiff")
    def _left_arm_relax(self):
        self.add_status("left arm relaxed")
        self.nao.arms.left_relax()
        self.nao.say("left arm relaxed")
    def _right_arm_stiff(self):
        self.add_status("right arm stiff")
        self.nao.arms.right_stiff()
        self.nao.say("right arm stiff")
    def _right_arm_relax(self):
        self.add_status("right arm relaxed")
        self.nao.arms.right_relax()
        self.nao.say("right arm relaxed")
    def _left_leg_stiff(self):
        self.add_status("left leg stiff")
        self.nao.legs.left_stiff()
        self.nao.say("left leg stiff")
    def _left_leg_relax(self):
        self.add_status("left leg relaxed")
        self.nao.legs.left_relax()
        self.nao.say("left leg relaxed")
    def _right_leg_stiff(self):
        self.add_status("right leg stiff")
        self.nao.legs.right_stiff()
        self.nao.say("right leg stiff")
    def _right_leg_relax(self):
        self.add_status("right leg relaxed")
        self.nao.legs.right_relax()
        self.nao.say("right leg relaxed")
    def _head_stiff(self):
        self.add_status("head stiff")
        self.nao.head.stiff()
        self.nao.say("head stiff")
    def _head_relax(self):
        self.add_status("head relaxed")
        self.nao.head.relax()
        self.nao.say("head relaxed")

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


    def _on_motors_off(self, instance):
        if self.connection:
            self.add_status('Turning NAO motors off')
            self.nao.relax()
            self.motors_on = False

    def _on_motors_on(self, instance):
        if self.connection:
            self.add_status('Turning NAO motors on')
            self.nao.stiff()
            self.motors_on = True

    def _on_run_script(self, instance):
        if self.connection:
            # TODO: run only selected code
            # code = self.codeinput.selection_text
            # if not code or len(code) == 0:
            code = self.codeinput.text
            self.nao.naoscript.run_script(code, '\n')

    def _on_add_keyframe(self, instance):
        if self.connection:
            # get angles
            angles = self.connection.joint_manager.get_joint_angles()
            print angles

            # translating
            translator = get_translator()
            commands = translator.detect_command(angles)
            command_str = translator.commands_to_text(commands)

            # update code view
            self.codeinput.text = "{}\r\n{}".format(self.codeinput.text, command_str)


    def on_files(self, instance, values):
        if not values[0]:
            return
        _file = codecs.open(values[0], 'r', encoding='utf8')
        self.codeinput.text = _file.read()
        _file.close()

    def on_action(self, instance, l):
        if self.connection:
            try:
                self.standard_positions[l]()
            except KeyError as e:
                print e


if __name__ == '__main__':
    NaoRecorderApp().run()
