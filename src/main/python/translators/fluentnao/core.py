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


COMMANDS = [

            # head
            CommandSpec('forward', 'head',
                        set(['HeadYaw']),
                        [Transform(linear, 'HeadYaw', 'headYaw', [1, 0])],
                        [Constraint(in_range, [-45, 45, 'HeadYaw'])],
                        ['headYaw']
                        ),
            CommandSpec('right', 'head',
                        set(['HeadYaw']),
                        [Transform(linear, 'HeadYaw', 'headYaw', [-1, -90])],
                        [Constraint(in_range, [-90, -46, 'HeadYaw'])],
                        ['headYaw']
                        ),
            CommandSpec('left', 'head',
                        set(['HeadYaw']),
                        [Transform(linear, 'HeadYaw', 'headYaw', [1, -90])],
                        [Constraint(in_range, [45, 90, 'HeadYaw'])],
                        ['headYaw']
                        ),

            CommandSpec('up', 'head',
                        set(['HeadPitch']),
                        [Transform(linear, 'HeadPitch', 'headPitch', [-1, -38])],
                        [Constraint(in_range, [-38, -10, 'HeadPitch'])],
                        ['headPitch']
                        ),
            CommandSpec('down', 'head',
                        set(['HeadPitch']),
                        [Transform(linear, 'HeadPitch', 'headPitch', [1, -29])],
                        [Constraint(in_range, [10, 29, 'HeadPitch'])],
                        ['headPitch']
                        ),
            CommandSpec('center', 'head',
                        set(['HeadPitch']),
                        [Transform(linear, 'HeadPitch', 'headPitch', [1, 0])],
                        [Constraint(in_range, [-11, 9, 'HeadPitch'])],
                        ['headPitch']
                        ),

            # arms both
            CommandSpec('forward', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
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
                        [Constraint(greater_than, [44, 'LShoulderRoll']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('up', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll', 'RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, -90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0]),
                         Transform(linear, 'RShoulderPitch', 'rpitch', [-1, -90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
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

            # arms right
            CommandSpec('right_forward', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [-45, 45, 'RShoulderPitch']),
                          Constraint(greater_than, [-45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_out', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 0]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, -90])],
                        [Constraint(less_than, [-45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),
            CommandSpec('right_up', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, -90]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [-110, -45, 'RShoulderPitch']),
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
            CommandSpec('right_back', 'arms',
                        set(['RShoulderPitch', 'RShoulderRoll']),
                        [Transform(linear, 'RShoulderPitch', 'rpitch', [-1, 119.5]),
                         Transform(linear, 'RShoulderRoll', 'rroll', [-1, 0])],
                        [Constraint(in_range, [96, 119.5, 'RShoulderPitch']),
                          Constraint(less_than, [45, 'RShoulderRoll'])],
                        ['rpitch', 'rroll']
                        ),

            # arms left
            CommandSpec('left_forward', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0])],
                        [Constraint(in_range, [-45, 45, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_out', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 0]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, -90])],
                        [Constraint(greater_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),
            CommandSpec('left_up', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, -90]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0])],
                        [Constraint(in_range, [-110, -45, 'LShoulderPitch']),
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
            CommandSpec('left_back', 'arms',
                        set(['LShoulderPitch', 'LShoulderRoll']),
                        [Transform(linear, 'LShoulderPitch', 'lpitch', [-1, 119.5]),
                         Transform(linear, 'LShoulderRoll', 'lroll', [1, 0])],
                        [Constraint(in_range, [96, 119.5, 'LShoulderPitch']),
                          Constraint(less_than, [45, 'LShoulderRoll'])],
                        ['lpitch', 'lroll']
                        ),

            # elbows both
            CommandSpec('bent', 'elbows',
                        set(['LElbowRoll', 'RElbowRoll']),
                        [Transform(linear, 'LElbowRoll', 'lroll', [1, 89]),
                         Transform(linear, 'RElbowRoll', 'rroll', [1, -89])],
                        [Constraint(less_than, [-43, 'LElbowRoll']),
                          Constraint(greater_than, [43, 'RElbowRoll']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['rroll']
                        ),
            CommandSpec('straight', 'elbows',
                        set(['LElbowRoll', 'RElbowRoll']),
                        [Transform(linear, 'LElbowRoll', 'lroll', [1, -0.5]),
                         Transform(linear, 'RElbowRoll', 'rroll', [1, 0.5])],
                        [Constraint(less_than, [43, 'LElbowRoll']),
                          Constraint(less_than, [43, 'RElbowRoll']),
                         Constraint(max_difference, [10, 'lroll', 'rroll'])],
                        ['rroll']
                        ),
            CommandSpec('turn_up', 'elbows',
                        set(['LElbowYaw', 'RElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [-1, -90]),
                         Transform(linear, 'RElbowYaw', 'ryaw', [1, -90])],
                        [Constraint(greater_than, [45, 'RElbowYaw']),
                          Constraint(less_than, [-45, 'LElbowYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),
            CommandSpec('turn_in', 'elbows',
                        set(['LElbowYaw', 'RElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [-1, 0]),
                         Transform(linear, 'RElbowYaw', 'ryaw', [1, 0])],
                        [Constraint(in_range, [-44, 44, 'RElbowYaw']),
                          Constraint(in_range, [-44, 44, 'LElbowYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),
            CommandSpec('turn_down', 'elbows',
                        set(['LElbowYaw', 'RElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [1, -90]),
                         Transform(linear, 'RElbowYaw', 'ryaw', [-1, -90])],
                        [Constraint(less_than, [-45, 'RElbowYaw']),
                          Constraint(greater_than, [45, 'LElbowYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),

            # elbows right
            CommandSpec('right_bent', 'elbows',
                        set(['RElbowRoll']),
                        [Transform(linear, 'RElbowRoll', 'rroll', [1, -89])],
                        [Constraint(greater_than, [43, 'RElbowRoll'])],
                        ['rroll']
                        ),
            CommandSpec('right_straight', 'elbows',
                        set(['RElbowRoll']),
                        [Transform(linear, 'RElbowRoll', 'rroll', [1, 0.5])],
                        [Constraint(less_than, [43, 'RElbowRoll'])],
                        ['rroll']
                        ),
            CommandSpec('right_turn_up', 'elbows',
                        set(['RElbowYaw']),
                        [Transform(linear, 'RElbowYaw', 'ryaw', [1, -90])],
                        [Constraint(greater_than, [45, 'RElbowYaw'])],
                        ['ryaw']
                        ),
            CommandSpec('right_turn_in', 'elbows',
                        set(['RElbowYaw']),
                        [Transform(linear, 'RElbowYaw', 'ryaw', [-1, 0])],
                        [Constraint(in_range, [-44, 44, 'RElbowYaw'])],
                        ['ryaw']
                        ),
            CommandSpec('right_turn_down', 'elbows',
                        set(['LElbowYaw', 'RElbowYaw']),
                        [Transform(linear, 'RElbowYaw', 'ryaw', [-1, -90])],
                        [Constraint(less_than, [-45, 'RElbowYaw'])],
                        ['ryaw']
                        ),

            # elbows left
            CommandSpec('left_bent', 'elbows',
                        set(['LElbowRoll']),
                        [Transform(linear, 'LElbowRoll', 'lroll', [-1, -89])],
                        [Constraint(less_than, [-43, 'LElbowRoll'])],
                        ['lroll']
                        ),
            CommandSpec('left_straight', 'elbows',
                        set(['LElbowRoll']),
                        [Transform(linear, 'LElbowRoll', 'lroll', [1, -0.5])],
                        [Constraint(less_than, [43, 'LElbowRoll'])],
                        ['lroll']
                        ),
            CommandSpec('left_turn_up', 'elbows',
                        set(['LElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [-1, -90])],
                        [Constraint(less_than, [-45, 'LElbowYaw'])],
                        ['lyaw']
                        ),
            CommandSpec('left_turn_in', 'elbows',
                        set(['LElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [1, 0])],
                        [Constraint(in_range, [-44, 44, 'LElbowYaw'])],
                        ['lyaw']
                        ),
            CommandSpec('left_turn_down', 'elbows',
                        set(['LElbowYaw', 'RElbowYaw']),
                        [Transform(linear, 'LElbowYaw', 'lyaw', [1, -90])],
                        [Constraint(greater_than, [45, 'LElbowYaw'])],
                        ['lyaw']
                        ),

            # wrists both
            CommandSpec('center', 'wrists',
                        set(['LWristYaw', 'RWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [1, 0]),
                         Transform(linear, 'RWristYaw', 'ryaw', [-1, 0])],
                        [Constraint(in_range, [-44, 44, 'LWristYaw']),
                          Constraint(in_range, [-44, 44, 'RWristYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),
            CommandSpec('turn_out', 'wrists',
                        set(['LWristYaw', 'RWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [1, -90]),
                         Transform(linear, 'RWristYaw', 'ryaw', [-1, -90])],
                        [Constraint(greater_than, [45, 'LWristYaw']),
                          Constraint(less_than, [-45, 'RWristYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),
            CommandSpec('turn_in', 'wrists',
                        set(['LWristYaw', 'RWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [-1, -90]),
                         Transform(linear, 'RWristYaw', 'ryaw', [1, -90])],
                        [Constraint(less_than, [-45, 'LWristYaw']),
                          Constraint(greater_than, [45, 'RWristYaw']),
                         Constraint(max_difference, [10, 'lyaw', 'ryaw'])],
                        ['ryaw']
                        ),

            # wrists left
            CommandSpec('left_center', 'wrists',
                        set(['LWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [1, 0])],
                        [Constraint(in_range, [-44, 44, 'LWristYaw'])],
                        ['lyaw']
                        ),
            CommandSpec('left_turn_out', 'wrists',
                        set(['LWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [1, -90])],
                        [Constraint(greater_than, [45, 'LWristYaw'])],
                        ['lyaw']
                        ),
            CommandSpec('left_turn_in', 'wrists',
                        set(['LWristYaw']),
                        [Transform(linear, 'LWristYaw', 'lyaw', [-1, -90])],
                        [Constraint(less_than, [-45, 'LWristYaw'])],
                        ['lyaw']
                        ),

            # wrists right
            CommandSpec('right_center', 'wrists',
                        set(['RWristYaw']),
                        [Transform(linear, 'RWristYaw', 'ryaw', [-1, 0])],
                        [Constraint(in_range, [-44, 44, 'RWristYaw'])],
                        ['ryaw']
                        ),
            CommandSpec('right_turn_out', 'wrists',
                        set(['RWristYaw']),
                        [Transform(linear, 'RWristYaw', 'ryaw', [-1, -90])],
                        [Constraint(less_than, [-45, 'RWristYaw'])],
                        ['ryaw']
                        ),
            CommandSpec('right_turn_in', 'wrists',
                        set(['RWristYaw']),
                        [Transform(linear, 'RWristYaw', 'ryaw', [1, -90])],
                        [Constraint(greater_than, [45, 'RWristYaw'])],
                        ['ryaw']
                        ),

            # hands both
            CommandSpec('open', 'hands',
                        set(['LHand', 'RHand']),
                        [],
                        [Constraint(greater_than, [17, 'LHand']),
                          Constraint(greater_than, [17, 'RHand'])],
                        []
                        ),
            CommandSpec('close', 'hands',
                        set(['LHand', 'RHand']),
                        [],
                        [Constraint(less_than, [17, 'LHand']),
                          Constraint(less_than, [17, 'RHand'])],
                        []
                        ),

            # hands right
            CommandSpec('right_open', 'hands',
                        set(['RHand']),
                        [],
                        [Constraint(greater_than, [17, 'RHand'])],
                        []
                        ),
            CommandSpec('right_close', 'hands',
                        set(['RHand']),
                        [],
                        [Constraint(less_than, [17, 'RHand'])],
                        []
                        ),

            # hands left
            CommandSpec('left_open', 'hands',
                        set(['LHand']),
                        [],
                        [Constraint(greater_than, [17, 'LHand'])],
                        []
                        ),
            CommandSpec('left_close', 'hands',
                        set(['LHand']),
                        [],
                        [Constraint(less_than, [17, 'LHand'])],
                        []
                        )
           ]


class FluentNaoTranslator(object):

    def commands_to_text(self, commands, is_blocking=False, fluentnao=None, keyframe_duration=None):
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

        if commands:
            prefix = ''
            if fluentnao:
                prefix = fluentnao

            if keyframe_duration:
                prefix = prefix + "set_duration({duration}).".format(duration=keyframe_duration)

            output = prefix + output

            if is_blocking:
                output = output + ".go()"

        return output

    def detect_command(self, joint_dict, changed_joint_names, enabled_joint_names):
        joints_degrees = joints_to_degrees(joint_dict, True)

        commands = []
        joints_done = set()
        cur_prefix = None

        for cs in COMMANDS:
            # check whether any of the joints used by this command have changed
            # we take the intersection of the command joints and the changed joints
            if changed_joint_names & cs.joints:
                # we can only produce commands that only depend on enabled joints
                # ignore all other commands using joints marked as done
                if cs.joints.issubset(enabled_joint_names) and not cs.joints.issubset(joints_done):
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
