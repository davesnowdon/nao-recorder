'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import math

class FluentNaoTranslator(object):
	def __init__(self):

		# command: (desired deg, max deg, min deg)
		self.commands_dict = {
			"arms.left_forward": {
				'LShoulderPitch': (0, 45, -45),
				'LShoulderRoll': (0, 45, -90)
			},
			"arms.right_forward": {
				'LShoulderPitch': (0, 45, -45),
				'LShoulderRoll': (0, 90, -45)
			}
		}


	def detect_command(self, joint_dict):
		score = {}
		commands = []

		# commands
		for command in self.commands_dict.keys():

			# command joint dict: desired, max and min
			cmd_joint_dict = self.commands_dict[command]

			# final command tuple
			cmd_tuple = (command, [0, 0]) 				 
			

			# joint degrees
			range_match = True
			for joint in cmd_joint_dict:

				# naos current position (passed in)
				deg_nao = math.degrees(joint_dict[joint])

				# range tuple
				cmd_range_tuple = cmd_joint_dict[joint]

				# set: desired, max & min
				deg_desired = cmd_range_tuple[0]
				deg_max = cmd_range_tuple[1]
				deg_min = cmd_range_tuple[2]

				# in range?
				print joint + ' ' + str(deg_min) + ' <= ' + str(deg_nao) + ' <= ' + str(deg_max)
				if deg_min <= deg_nao <= deg_max:

					# offset
					offset = caculate_offset(deg_desired, deg_nao, joint)

					# assign to cmd tuple
					assign_offset(joint, cmd_tuple)

				# not in range?
				else:
					range_match = False

			# use command
			if range_match:
				commands.append(cmd_tuple)

		# return all commands needed for arms
		return commands #reduce_commands(commands)

	#def reduce_commands(commands):
    #
	#	for cmd_tuple in commands:
	#		m = [cmd for x in l where x[0] == 'a']



	def assign_offset(joint, cmd_tuple):

		# Roll?
		if (joint.find('Roll') > -1):
			
			# first offset
			cmd_tuple[1][1] = offset

		else:

			# second offset
			cmd_tuple[1][0] = offset

	def caculate_offset(deg_desired, deg_nao, joint):

		# Roll?
		if (joint.find('Roll') > -1):
			
			# Left?
			if (joint.startswith('L')):
				return deg_desired + deg_nao

		# default offset calculation
		return deg_desired - deg_nao

	def is_left_arm_forward(self, joint_dict):

		# left arm
		l_should_pitch = math.degrees(joint_dict['LShoulderPitch'])
		l_should_roll = math.degrees(joint_dict['LShoulderRoll'])

		# left pitch range(90)
		if l_should_pitch <= 45 and l_should_pitch >= -45:
			l_pitch_offset = 0 + l_should_pitch 

			# LEFT: match roll
			if l_should_roll <= 45:
				l_roll_offset = 0 + l_should_roll
				return ("arms.left_forward", [l_pitch_offset, l_roll_offset]) 
		return None

	def is_right_arm_forward(self, joint_dict):

		# right arm
		r_should_pitch = math.degrees(joint_dict['RShoulderPitch'])
		r_should_roll = math.degrees(joint_dict['RShoulderRoll'])

		# RIGHT: match pitch
		if r_should_pitch <= 45 and r_should_pitch >= -45:
			r_pitch_offset = 0 + r_should_pitch 

			# LEFT: match roll
			if r_should_roll >= -45:
				r_roll_offset = 0 + r_should_roll
				return ("arms.right_forward", [r_pitch_offset, r_roll_offset])
		return None

	def is_arms_forward(self, joint_dict):
		# check each arm
		left = self.is_left_arm_forward(joint_dict)
		right = self.is_right_arm_forward(joint_dict)

		# both forward?
		if left and right:
			# get offset (same for left or right)
			pitch_offset = left[1][0]
			roll_offset = left[1][1]
			return ("arms.forward", [pitch_offset, roll_offset])
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
