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
from kivy.uix.popup import Popup
from kivy.properties import ListProperty
from kivy.core.window import Window

from pygments import lexers
from pygame import font as fonts
import codecs, os

import naoutil.naoenv as naoenv
import fluentnao.nao as nao

class Fnt_SpinnerOption(SpinnerOption):
    pass

class LoadDialog(Popup):

    def load(self, path, selection):
        self.choosen_file = [None, ]
        self.choosen_file = selection
        Window.title = selection[0][selection[0].rfind(os.sep)+1:]
        self.dismiss()

    def cancel(self):
        self.dismiss()


class SaveDialog(Popup):

    def save(self, path, selection):
        _file = codecs.open(selection, 'w', encoding='utf8')
        _file.write(self.text)
        Window.title = selection[selection.rfind(os.sep)+1:]
        _file.close()
        self.dismiss()

    def cancel(self):
        self.dismiss()

class NaoRecorderApp(App):

    files = ListProperty([None, ])

    def build(self):

        # connect to nao
        self._make_environment()

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
            values=('Open', 'SaveAs', 'Save', 'Close'))
        mnu_file.bind(text=self._file_menu_selected)

        # motors on/off
        btn_motors_on = Button(text='motors on')
        btn_motors_on.bind(on_press=self._on_motors_on)

        btn_motors_off = Button(text='motors off')
        btn_motors_off.bind(on_press=self._on_motors_off)

        # root actions menu
        self.standard_positions = {
            'stand_init': self.nao.stand_init, 
            'sit_relax': self.nao.sit_relax, 
            'stand_zero': self.nao.stand_zero, 
            'lying_belly': self.nao.lying_belly, 
            'lying_back': self.nao.lying_back, 
            'stand': self.nao.stand, 
            'crouch': self.nao.crouch, 
            'sit': self.nao.sit
        }
        robot_actions = Spinner(
            text='action',
            values=sorted(self.standard_positions.keys()))
        robot_actions.bind(text=self.on_action)

        # add to menu
        menu.add_widget(mnu_file)
        menu.add_widget(btn_motors_on)
        menu.add_widget(btn_motors_off)
        menu.add_widget(robot_actions)
        b.add_widget(menu)

        self.codeinput = CodeInput(
            lexer=lexers.PythonLexer(),
            font_name='data/fonts/DroidSansMono.ttf', font_size=12,
            text="")

        b.add_widget(self.codeinput)

        return b

    def _make_environment(self):
        # nao util environment
        self.env = naoenv.make_environment(None, ipaddr="nao.local", port=9559)

        # fluent nao
        self.nao = nao.Nao(self.env, None)

    def _update_size(self, instance, size):
        self.codeinput.font_size = float(size)

    def _update_font(self, instance, fnt_name):
        instance.font_name = self.codeinput.font_name =\
            fonts.match_font(fnt_name)

    def _file_menu_selected(self, instance, value):
        if value == 'File':
            return
        instance.text = 'File'
        if value == 'Open':
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
        print 'nao motors off'
        self.nao.relax()

    def _on_motors_on(self, instance):
        print 'nao motors on'
        self.nao.stiff()

    def on_files(self, instance, values):
        if not values[0]:
            return
        _file = codecs.open(values[0], 'r', encoding='utf8')
        self.codeinput.text = _file.read()
        _file.close()

    def on_action(self, instance, l):

        try:

            # run standard position
            self.standard_positions[l]()
            
        except KeyError as e:
            print e

        
if __name__ == '__main__':
    NaoRecorderApp().run()