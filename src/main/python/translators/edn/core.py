'''
Created on 12 Feb 2014

@author: davesnowdon
'''

from pygments import lexers

import edn_format

class EDNTranslator(object):
    def __init__(self):
        super(EDNTranslator, self).__init__()
        self.name = 'EDN'
        self.is_reversible = True
        self.is_runnable = False
        self.lexer = lexers.ClojureLexer()

    def generate(self, joint_dict, changed_joint_names, enabled_joint_names,
                 is_blocking=False, keyframe_duration=None, **kwargs):
        if changed_joint_names:
            changed_joints = {}
            for j in changed_joint_names:
                changed_joints[j] = joint_dict[j]

            state = {}
            for j in enabled_joint_names:
                state[j] = joint_dict[j]

            edn_map = { "is_blocking" : is_blocking,
                         "state" : state,
                         "changes" : changed_joints }

            if keyframe_duration:
                edn_map["duration"] = keyframe_duration

            return edn_format.dumps(edn_map)
        else:
            return ''

    def append(self, code, new_command):
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

    def parse(self, code):
        return edn_format.loads(code)