'''
Created on 4 Dec 2013

@author: davesnowdon
'''

import json

class JsonTranslator(object):

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
