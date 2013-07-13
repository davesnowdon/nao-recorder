'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import collections
from sets import Set

from recorder.JointManager import joints_to_degrees

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
                        Set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
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
                        Set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, -90]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, -90])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(greater_than, [44, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lpitch', 'rpitch']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('up', 'arms',
                        Set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
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
            CommandSpec('left_forward', 'arms',
                        Set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('right_forward', 'arms',
                        Set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('left_out', 'arms',
                        Set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, -90])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(greater_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('right_out', 'arms',
                        Set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, -90])],
                        [Constraint(in_range, [-45, 45, 'RShoulderPitch']),
                          Constraint(less_than, [-45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('left_up', 'arms',
                        Set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, -90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [-1, 0])],
                        [Constraint(in_range, [-110, -45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('right_up', 'arms',
                        Set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, -90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [1, 0])],
                        [Constraint(in_range, [-110, -45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
           ]


class Algo2Translator(object):

    def detect_command(self, joint_dict):

        commands = []

        joints_degrees = joints_to_degrees(joint_dict, True)

        joints_done = Set()

        cur_prefix = None

        for cs in COMMANDS:
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
        command_parameters = []
        for p in cs.parameters:
            command_parameters.append(cdata[p])

        if cur_prefix == cs.prefix:
            return (cs.command, command_parameters)
        else:
            return ("{}.{}".format(cs.prefix, cs.command), command_parameters)
