'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import math

class FluentNaoTranslator(object):
	def detect_command(self, joint_dict):
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
			else: 
				# out or up?
				pass

			# check right
			right = self.is_right_arm_forward(joint_dict)	
			if right:
				commands.append(right)
			else:
				# out or up?
				pass

		# return all commands needed for arms
		return commands

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
