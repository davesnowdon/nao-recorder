'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import algo2translator
from algo2translator import Algo2Translator
from drytranslator import DryTranslator

class FluentNaoTranslator(object):

    def detect_command(self, joint_dict):
        # return DryTranslator().detect_command(joint_dict)
        return Algo2Translator().detect_command(joint_dict)

    def commands_to_text(self, commands):
        """
        Takes a list of commands and converts them to text
        """
        output = ""
        for command_tuple in commands:
            # the command
            if not output == "":
                 output = output + "."

            args = [str(p) for p in command_tuple[1]]
            command_str = "{cmd}({params})".format(cmd=command_tuple[0], params=",".join(args))
            output = output + command_str

        return output

