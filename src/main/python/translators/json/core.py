'''
Created on 4 Dec 2013

@author: davesnowdon
'''

import json

class JsonTranslator(object):
    def __init__(self):
        super(JsonTranslator, self).__init__()
        self.name = 'JSON'
        self.is_reversible = True
        self.is_runnable = False

    def commands_to_text(self, commands, is_blocking=False, keyframe_duration=None, **kwargs):
        """
        Takes a list of commands and converts them to text
        """
        if commands:
            joints = {}
            for cmd_tuple in commands:
                joint_name = cmd_tuple[0]
                joint_value = cmd_tuple[1][0]
                joints[joint_name] = joint_value

            json_map = { "is_blocking" : is_blocking,
                         "changes" : joints }

            if keyframe_duration:
                json_map["duration"] = keyframe_duration

            return json.dumps(json_map)
        else:
            return ""


    def detect_command(self, joint_dict, changed_joint_names, enabled_joint_names):
        commands = []

        for j in changed_joint_names:
            cmd = (j, [joint_dict[j]])
            commands.append(cmd)

        return commands

    def append_command(self, code, new_command):
        if code.strip():
            if new_command:
                # remove any enclosing square brackets
                code = code.strip().lstrip('[').rstrip(']').strip()
                # add a comma after the existing code and replace square brackets
                return "[\r\n{},\r\n{}\r\n]".format(code, new_command)
            else:
                return code
        else:
            if new_command:
                return "[\r\n{}\r\n]".format(new_command)
            else:
                return ''

    def parse_commands(self, code):
        return json.loads(code)