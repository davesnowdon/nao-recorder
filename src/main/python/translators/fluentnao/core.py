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

		# arms forward?
		arms_commands = self.eval_forward(joint_dict)

		# arms out?
		arms_out_args = {
			'both_command': 'arms.out',
			'left': {
				'command': 'arms.left_out',
				'pitch_joint':'LShoulderPitch',
				'roll_joint':'LShoulderRoll',
				'pitch_max':45,
				'pitch_min':-45,
				'roll_max':110,
				'roll_min':45,
				'offset_pitch_lambda': lambda x: round(-x),
				'offset_roll_lambda': lambda x: round(x - 90)
			},
			'right': {
				'command': 'arms.right_out',
				'pitch_joint':'RShoulderPitch',
				'roll_joint':'RShoulderRoll',
				'pitch_max':45,
				'pitch_min':-45,
				'roll_max':-45,
				'roll_min':-110,
				'offset_pitch_lambda': lambda x: round(-x),
				'offset_roll_lambda': lambda x: round(-x - 90)
			}
		}
		arms_commands = arms_commands + self.eval_algo(joint_dict, arms_out_args)

		# arms up?
		arms_up_args = {
			'both_command': 'arms.up',
			'left': {
				'command': 'arms.left_up',
				'pitch_joint':'LShoulderPitch',
				'roll_joint':'LShoulderRoll',
				'pitch_max':-45,
				'pitch_min':-110,
				'roll_max':45,
				'roll_min':-90,
				'offset_pitch_lambda': lambda x: round(-90 - x),
				'offset_roll_lambda': lambda x: round(-x)
			},
			'right': {
				'command': 'arms.right_up',
				'pitch_joint':'RShoulderPitch',
				'roll_joint':'RShoulderRoll',
				'pitch_max':-45,
				'pitch_min':-110,
				'roll_max':90,
				'roll_min':-45,
				'offset_pitch_lambda': lambda x: round(-90 - x),
				'offset_roll_lambda': lambda x: round(x)
			}
		}
		arms_commands = arms_commands + self.eval_algo(joint_dict, arms_up_args)

		# arms back?

		return arms_commands


	def is_algo(self, joint_dict, args):

		# left pitch and roll
		l_pitch = math.degrees(joint_dict[args['pitch_joint']])
		l_roll = math.degrees(joint_dict[args['roll_joint']])

		# left pitch
		#print "{0} <= {1} <= {2}: {3}".format(args['pitch_min'], l_pitch, args['pitch_max'], args['pitch_joint'])
		if args['pitch_min'] <= l_pitch <= args['pitch_max']:
			l_pitch_offset = args['offset_pitch_lambda'](l_pitch)

			# LEFT: match roll
			#print "{0} <= {1} <= {2}: {3}".format(args['roll_min'], l_roll, args['roll_max'], args['roll_joint'])
			if args['roll_min'] <= l_roll <= args['roll_max']:
				l_roll_offset = args['offset_roll_lambda'](l_roll)
				return (args['command'], [l_pitch_offset, l_roll_offset]) 
		return None

	def eval_algo(self, joint_dict, args):
		commands = []

		# check both
		result = self.is_algo_both(joint_dict, args)
		if result:
			commands.append(result)
		else:
			# check left
			left = self.is_algo(joint_dict, args['left'])
			if left:
				commands.append(left)
			
			# check right
			right = self.is_algo(joint_dict, args['right'])	
			if right:
				commands.append(right)
		return commands

	def is_algo_both(self, joint_dict, args):
		# check each arm
		left = self.is_algo(joint_dict, args['left'])
		right = self.is_algo(joint_dict, args['right'])
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





	# TODO: make this generic later
	def eval_forward(self, joint_dict):
		commands = []

		# check both arms
		result = self.is_arms_forward(joint_dict)
		if result:
			commands.append(result)
		else:
			# check left
			left = self.is_left_arm_forward(joint_dict)
			if left:
				commands.append(left)
			
			# check right
			right = self.is_right_arm_forward(joint_dict)	
			if right:
				commands.append(right)
		return commands

	def is_left_arm_forward(self, joint_dict):

		# left arm
		l_should_pitch = math.degrees(joint_dict['LShoulderPitch'])
		l_should_roll = math.degrees(joint_dict['LShoulderRoll'])

		# left pitch range(90)
		if l_should_pitch <= 45 and l_should_pitch >= -45:
			l_pitch_offset = round(l_should_pitch)

			# LEFT: match roll
			if l_should_roll <= 45:
				l_roll_offset = round(-l_should_roll)
				return ("arms.left_forward", [l_pitch_offset, l_roll_offset]) 
		return None

	def is_right_arm_forward(self, joint_dict):

		# right arm
		r_should_pitch = math.degrees(joint_dict['RShoulderPitch'])
		r_should_roll = math.degrees(joint_dict['RShoulderRoll'])

		# RIGHT: match pitch
		if r_should_pitch <= 45 and r_should_pitch >= -45:
			r_pitch_offset = round(r_should_pitch)

			# LEFT: match roll
			if r_should_roll >= -45:
				r_roll_offset = round(r_should_roll)
				return ("arms.right_forward", [r_pitch_offset, r_roll_offset])
		return None

	def is_arms_forward(self, joint_dict):
		# check each arm
		left = self.is_left_arm_forward(joint_dict)
		right = self.is_right_arm_forward(joint_dict)

		# both forward?
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
				return ("arms.forward", [l_pitch_offset, l_roll_offset])

		return None
#>>> nao.arms.right_forward()
#'RShoulderRoll': 0
#'RShoulderPitch': 0

#>>> nao.arms.right_out()
#'RShoulderPitch': 0
#'RShoulderRoll': -90

#>>> nao.arms.right_up()
#'RShoulderPitch': -90
#'RShoulderRoll': 0
