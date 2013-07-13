'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import math

class FluentNaoTranslator(object):

	def detect_command(self, joint_dict):
		commands = []

		# arms
		commands = commands + self.detect_arms(joint_dict)

		# return
		return commands

	def detect_arms(self, joint_dict):

		arms_commands = []

		# arms forward?
		arms_forward_args = {
			'both_command': 'arms.forward',
			'left': {
				'command': 'arms.left_forward',
				'pitch_joint':'LShoulderPitch',
				'pitch_max':45,
				'pitch_min':-45,
				'pitch_offset_lambda': lambda x: round(x),
				'roll_joint':'LShoulderRoll',
				'roll_max':45,
				'roll_min':-90,
				'roll_offset_lambda': lambda x: round(-x)
			},
			'right': {
				'command': 'arms.right_forward',
				'pitch_joint':'RShoulderPitch',
				'pitch_max':45,
				'pitch_min':-45,
				'pitch_offset_lambda': lambda x: round(x),
				'roll_joint':'RShoulderRoll',
				'roll_max':90,
				'roll_min':-45,
				'roll_offset_lambda': lambda x: round(x)
			}
		}
		arms_commands = arms_commands + self.eval_commands(joint_dict, arms_forward_args)

		# arms out?
		arms_out_args = {
			'both_command': 'arms.out',
			'left': {
				'command': 'arms.left_out',
				'pitch_joint':'LShoulderPitch',
				'pitch_max':45,
				'pitch_min':-45,
				'pitch_offset_lambda': lambda x: round(-x),
				'roll_joint':'LShoulderRoll',
				'roll_max':110,
				'roll_min':45,
				'roll_offset_lambda': lambda x: round(x - 90)
			},
			'right': {
				'command': 'arms.right_out',
				'pitch_joint':'RShoulderPitch',
				'pitch_max':45,
				'pitch_min':-45,
				'pitch_offset_lambda': lambda x: round(-x),
				'roll_joint':'RShoulderRoll',
				'roll_max':-45,
				'roll_min':-110,
				'roll_offset_lambda': lambda x: round(-x - 90)
			}
		}
		arms_commands = arms_commands + self.eval_commands(joint_dict, arms_out_args)

		# arms up?
		arms_up_args = {
			'both_command': 'arms.up',
			'left': {
				'command': 'arms.left_up',
				'pitch_joint':'LShoulderPitch',
				'pitch_max':-45,
				'pitch_min':-110,
				'pitch_offset_lambda': lambda x: round(-90 - x),
				'roll_joint':'LShoulderRoll',
				'roll_max':45,
				'roll_min':-90,
				'roll_offset_lambda': lambda x: round(-x)
			},
			'right': {
				'command': 'arms.right_up',
				'pitch_joint':'RShoulderPitch',
				'pitch_max':-45,
				'pitch_min':-110,
				'pitch_offset_lambda': lambda x: round(-90 - x),
				'roll_joint':'RShoulderRoll',
				'roll_max':90,
				'roll_min':-45,
				'roll_offset_lambda': lambda x: round(x)
			}
		}
		arms_commands = arms_commands + self.eval_commands(joint_dict, arms_up_args)

		# arms back?

		return arms_commands

	def eval_commands(self, joint_dict, args):
		commands = []

		# check both
		result = self.is_both_commands(joint_dict, args)
		if result:
			commands.append(result)
		else:
			# check left
			left = self.is_command(joint_dict, args['left'])
			if left:
				commands.append(left)
			
			# check right
			right = self.is_command(joint_dict, args['right'])	
			if right:
				commands.append(right)
		return commands

	def is_both_commands(self, joint_dict, args):
		# check each arm
		left = self.is_command(joint_dict, args['left'])
		right = self.is_command(joint_dict, args['right'])
		#print 'left {0}'.format(left)
		#print 'right {0}'.format(right)
		# both up?
		if left and right:
			
			# compare offsets
			l_pitch_offset = left[1][0]
			l_roll_offset = left[1][1]
			r_pitch_offset = right[1][0]
			r_roll_offset = right[1][1]

			# allow within 10 degrees
			pitch_diff = abs(l_pitch_offset - r_pitch_offset)
			roll_diff = abs(l_roll_offset - r_roll_offset)
			if pitch_diff <= 10 and roll_diff <= 10:

				# reduce
				return (args['both_command'], [l_pitch_offset, l_roll_offset])

		return None

	def is_command(self, joint_dict, args):

		# left pitch and roll
		l_pitch = math.degrees(joint_dict[args['pitch_joint']])
		l_roll = math.degrees(joint_dict[args['roll_joint']])

		# left pitch
		#print "{0} <= {1} <= {2}: {3}".format(args['pitch_min'], l_pitch, args['pitch_max'], args['pitch_joint'])
		if args['pitch_min'] <= l_pitch <= args['pitch_max']:
			l_pitch_offset = args['pitch_offset_lambda'](l_pitch)

			# LEFT: match roll
			#print "{0} <= {1} <= {2}: {3}".format(args['roll_min'], l_roll, args['roll_max'], args['roll_joint'])
			if args['roll_min'] <= l_roll <= args['roll_max']:
				l_roll_offset = args['roll_offset_lambda'](l_roll)
				return (args['command'], [l_pitch_offset, l_roll_offset]) 
		return None
