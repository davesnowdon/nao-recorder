'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import collections

from recorder.core import joints_to_degrees

DEFAULT_FRAME_TIME = 0

Constraint = collections.namedtuple('Constraint',
                                    ['predicate', 'parameters'])

Transform = collections.namedtuple('Transform',
                                   ['operator', 'inval', 'outval', 'parameters'])

CommandSpec = collections.namedtuple('CommandSpec',
                                     ['command', 'prefix', 'joints', 'transforms',
                                      'constraints', 'parameters'])


def linear(value, params):
    return value * params[0] + params[1]


def in_range(joints, params):
    minval = params[0]
    maxval = params[1]
    names = params[2:]
    for n in names:
        v = joints[n]
        if (v < minval) or (v > maxval):
            return False
    return True

def less_than(joints, params):
    maxval = params[0]
    names = params[1:]
    for n in names:
        if joints[n] > maxval:
            return False
    return True

def greater_than(joints, params):
    minval = params[0]
    names = params[1:]
    for n in names:
        if joints[n] <= minval:
            return False
    return True

def max_difference(joints, params):
    max_diff = params[0]
    first = joints[params[1]]
    names = params[2:]
    for n in names:
        if abs(joints[n] - first) > max_diff:
            return False
    return True


COMMANDS = [CommandSpec('forward', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(less_than, [46, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),

            CommandSpec('out', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, -90]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, -90])],
                        [   # Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(greater_than, [44, 'LShoulderRoll']),
                         # Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),

            CommandSpec('up', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, -90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, -90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-110, -45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),

            CommandSpec('down', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [46, 95, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),

            CommandSpec('back', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 119.5]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 119.5]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [96, 119.5, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),

            # right
            CommandSpec('right_out', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, -90])],
                        [   # Constraint(in_range, [-45, 45, 'RShoulderPitch']),
                          Constraint(less_than, [-45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_back', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 119.5]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [96, 119.5, 'RShoulderPitch']),
                          Constraint(less_than, [45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_down', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [46, 95, 'RShoulderPitch']),
                          Constraint(less_than, [45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_forward', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-45, 45, 'RShoulderPitch']),
                          Constraint(greater_than, [-45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_up', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, -90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-110, -45, 'RShoulderPitch']),
                          Constraint(less_than, [45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),

            # left
            CommandSpec('left_out', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, -90])],
                        [   # Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(greater_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_back', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 119.5]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0])],
                        [Constraint(in_range, [96, 119.5, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_down', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0])],
                        [Constraint(in_range, [46, 95, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_forward', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_up', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, -90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0])],
                        [Constraint(in_range, [-110, -45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),

            CommandSpec('open', 'hands',
                        set(['LHand', 'RHand']),
                        [],
                        [Constraint(greater_than, [0.5, 'LHand']),
                          Constraint(greater_than, [0.5, 'RHand'])],
                        []
                        ),

            CommandSpec('close', 'hands',
                        set(['LHand', 'RHand']),
                        [],
                        [Constraint(less_than, [0.5, 'LHand']),
                          Constraint(less_than, [0.5, 'RHand'])],
                        []
                        ),

            CommandSpec('right_open', 'hands',
                        set(['RHand']),
                        [],
                        [Constraint(greater_than, [0.5, 'RHand'])],
                        []
                        ),

            CommandSpec('right_close', 'hands',
                        set(['RHand']),
                        [],
                        [Constraint(less_than, [0.3, 'RHand'])],
                        []
                        ),

            CommandSpec('left_open', 'hands',
                        set(['LHand']),
                        [],
                        [Constraint(greater_than, [0.5, 'LHand'])],
                        []
                        ),

            CommandSpec('left_close', 'hands',
                        set(['LHand']),
                        [],
                        [Constraint(less_than, [0.3, 'LHand'])],
                        []
                        )
           ]


class FluentNaoTranslator(object):

    def commands_to_text(self, commands, is_blocking=False, fluentnao=None):
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

        if fluentnao:
            output = fluentnao + output

        if is_blocking:
            output = output + ".go()"

        return output

    def detect_command(self, joint_dict, changed_joint_names):
        joints_degrees = joints_to_degrees(joint_dict, True)
        commands = []
        joints_done = set()
        cur_prefix = None

        for cs in COMMANDS:
            # check whether any of the joints used by this command have changed
            # we take the intersection of the command joints and the changed joints
            if changed_joint_names & cs.joints:
                # ignore all other commands using joints marked as done
                if not cs.joints.issubset(joints_done):
                    cdata = joints_degrees.copy()
                    self.do_transforms(cs, cdata)
                    if self.constraints_pass(cs, cdata):
                        joints_done = joints_done.union(cs.joints)
                        commands.append(self.generate_command(cs, cur_prefix, cdata))
                        cur_prefix = cs.prefix
        return commands

    def do_transforms(self, cs, cdata):
        for t in cs.transforms:
            cdata[t.outval] = round(t.operator(cdata[t.inval], t.parameters))

    def constraints_pass(self, cs, cdata):
        for c in cs.constraints:
            if not c.predicate(cdata, c.parameters):
                return False
        return True

    def generate_command(self, cs, cur_prefix, cdata):
        command_parameters = [DEFAULT_FRAME_TIME]
        for p in cs.parameters:
            command_parameters.append(cdata[p])

        if cur_prefix == cs.prefix:
            return (cs.command, command_parameters)
        else:
            return ("{}.{}".format(cs.prefix, cs.command), command_parameters)
