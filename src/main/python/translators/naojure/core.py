'''
Created on 9 Feb 2014

@author: davesnowdon
'''

from translators.fluentnao.core import FluentNaoTranslator

COMMAND_TO_KEYWORD = {'forward' : ':forward',
                      'right' : ':right',
                      'left' : ':left',
                      'up' : ':up',
                      'down' : ':down',
                      'center' : 'centre',
                      'out' : ':out',
                      'back' : ':back',
                      'right_forward' : ':right-forward',
                      'right_out' : ':right-out',
                      'right_up' : ':right-up',
                      'right_down' : ':right-down',
                      'right_back' : ':right-back',
                      'left_forward' : ':left-forward',
                      'left_out' : ':left-out',
                      'left_up' : ':left-up',
                      'left_down' : ':left-down',
                      'left_back' : ':left-back',
                      'bent' : ':bent',
                      'straight' : ':straight',
                      'turn_up' : ':turn-up',
                      'turn_in' : ':turn-in',
                      'turn_down' : ':turn-down',
                      'right_bent' : ':right-bent',
                      'right_straight' : ':right-straight',
                      'right_turn_up' : ':right-turn-up',
                      'right_turn_in' : ':right-turn-in',
                      'right_turn_down' : ':right-turn-down',
                      'left_bent' : ':left-bent',
                      'left_straight' : ':left-straight',
                      'left_turn_up' : ':left-turn-up',
                      'left_turn_in' : ':left-turn-in',
                      'left_turn_down' : ':left-turn-down',
                      'turn_out' : ':turn-out',
                      'left_center' : ':left-centre',
                      'left_turn_out' : ':left-turn-out',
                      'left_turn_in' : ':left-turn-in',
                      'right_center' : ':right-centre',
                      'right_turn_out' : ':right-turn-out',
                      'right_turn_in' : ':right-turn-in',
                      'open' : ':open',
                      'close' : ':close',
                      'right_open' : ':right-open',
                      'right_close' : ':right-close',
                      'left_open' : ':left-open',
                      'left_close' : ':left-close',
                      'point_toes' : ':point-toes',
                      'raise_toes' : ':raise-toes',
                      'left_point_toes' : ':left-point-toes',
                      'left_raise_toes' : ':left-raise-toes',
                      'right_point_toes' : ':right-point-toes',
                      'right_raise_toes' : ':right-raise-toes'
                      }

class NaojureTranslator(object):
    def __init__(self):
        super(NaojureTranslator, self).__init__()
        self.name = 'Naojure'
        self.is_reversible = False
        # TODO implement connection to nrepl server to allow naojure code to be run
        self.is_runnable = False
        self.fluentnao = FluentNaoTranslator()

    def generate(self, joint_dict, changed_joint_names, enabled_joint_names, **kwargs):
        # reuse FluentNAO code to decide on commands
        commands = self.fluentnao.detect_command(joint_dict, changed_joint_names, enabled_joint_names)

        # generate commands in naojure format
        command_str = self.commands_to_text(commands,
                                            keyframe_duration=kwargs['keyframe_duration'])
        return command_str

    def commands_to_text(self, commands, keyframe_duration=None):
        """
        Takes a list of commands and converts them to text
        """
        output = ""
        last_prefix = ''
        for command_tuple in commands:
            # format: (prefix command param1 param2)
            # separate prefix and commands
            # map prefix and command to function and keyword
            # ignore first parameter
            # skip other parameters if zero

            print command_tuple[0]
            args = [str(p) for p in command_tuple[1]]
            f_prefix_cmd = command_tuple[0].split('.')
            if len(f_prefix_cmd) > 1:
                last_prefix = f_prefix = f_prefix_cmd[0]
                f_cmd = f_prefix_cmd[1]
            else:
                f_prefix = last_prefix
                f_cmd = f_prefix_cmd[0]
            print "parsed = {} {}".format(f_prefix, f_cmd)
            n_keyword = COMMAND_TO_KEYWORD[f_cmd]
            command_str = "({cmd} {keyword} {params}) ".format(cmd=f_prefix, keyword=n_keyword, params=" ".join(args[1:]))
            output = output + command_str

        if commands:
            prefix = '(nao/donao robot '
            suffix = ' )'

            if keyframe_duration:
                prefix = prefix + ":duration {duration} ".format(duration=keyframe_duration)

            output = prefix + output + suffix

        return output

    def append(self, code, new_command):
        if new_command:
            if code:
                return "{}\r\n{}".format(code, new_command)
            else:
                return new_command
        else:
            return code
