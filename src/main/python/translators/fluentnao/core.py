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
		arms_commands = arms_commands + self.eval_out(joint_dict)

		# arms up?
 		arms_commands = arms_commands + self.eval_up(joint_dict)

		# arms back?

		return arms_commands

	def eval_out(self, joint_dict):
		commands = []

		# check both arms
		result = self.is_arms_out(joint_dict)
		if result:
			commands.append(result)
		else:
			# check left
			left = self.is_left_arm_out(joint_dict)
			if left:
				commands.append(left)
			
			# check right
			right = self.is_right_arm_out(joint_dict)	
			if right:
				commands.append(right)
		return commands

	def is_left_arm_out(self, joint_dict):

		# left arm
		l_should_pitch = math.degrees(joint_dict['LShoulderPitch'])
		l_should_roll = math.degrees(joint_dict['LShoulderRoll'])

		# left pitch
		if -45 <= l_should_pitch <= 45:
			l_pitch_offset = round(-l_should_pitch)

			# LEFT: match roll
			if l_should_roll >= 45:
				l_roll_offset = round(l_should_roll - 90)
				return ("arms.left_out", [l_pitch_offset, l_roll_offset]) 
		return None

	def is_right_arm_out(self, joint_dict):

		# right arm
		r_should_pitch = math.degrees(joint_dict['RShoulderPitch'])
		r_should_roll = math.degrees(joint_dict['RShoulderRoll'])

		# RIGHT: match pitch
		if -45 <= r_should_pitch <= 45:
			r_pitch_offset = round(-r_should_pitch)

			# LEFT: match roll
			if r_should_roll <= -45:
				r_roll_offset = round(-r_should_roll - 90)
				return ("arms.right_out", [r_pitch_offset, r_roll_offset])
		return None

	def is_arms_out(self, joint_dict):
		# check each arm
		left = self.is_left_arm_out(joint_dict)
		right = self.is_right_arm_out(joint_dict)

		# both out?
		if left and right:
			
			# compare offsets
			l_pitch_offset = left[1][0]
			l_roll_offset = left[1][1]
			r_pitch_offset = right[1][0]
			r_roll_offset = right[1][1]

			# allow within 10 degrees
			pitch_diff = abs(l_pitch_offset - r_pitch_offset)
			roll_diff = abs(l_roll_offset - r_roll_offset)
			print "{0} {1}".format(pitch_diff, roll_diff)
			if pitch_diff <= 10 and roll_diff <= 10:

				# reduce
				return ("arms.out", [l_pitch_offset, l_roll_offset])

		return None

	def eval_up(self, joint_dict):
		commands = []

		# check both arms
		result = self.is_arms_up(joint_dict)
		if result:
			commands.append(result)
		else:
			# check left
			left = self.is_left_arm_up(joint_dict)
			if left:
				commands.append(left)
			
			# check right
			right = self.is_right_arm_up(joint_dict)	
			if right:
				commands.append(right)
		return commands

	def is_left_arm_up(self, joint_dict):

		# left arm
		l_should_pitch = math.degrees(joint_dict['LShoulderPitch'])
		l_should_roll = math.degrees(joint_dict['LShoulderRoll'])

		# left pitch range(90)
		if l_should_pitch <= -45 and l_should_pitch >= -110:
			l_pitch_offset = round(-90 - l_should_pitch)

			# LEFT: match roll
			if l_should_roll <= 45:
				l_roll_offset = round(-l_should_roll)
				return ("arms.left_up", [l_pitch_offset, l_roll_offset]) 
		return None

	def is_right_arm_up(self, joint_dict):

		# right arm
		r_should_pitch = math.degrees(joint_dict['RShoulderPitch'])
		r_should_roll = math.degrees(joint_dict['RShoulderRoll'])

		# RIGHT: match pitch
		if r_should_pitch <= -45 and r_should_pitch >= -110:
			r_pitch_offset = round(-90 - r_should_pitch)

			# LEFT: match roll
			if r_should_roll >= -45:
				r_roll_offset = round(r_should_roll)
				return ("arms.right_up", [r_pitch_offset, r_roll_offset])
		return None

	def is_arms_up(self, joint_dict):
		# check each arm
		left = self.is_left_arm_up(joint_dict)
		right = self.is_right_arm_up(joint_dict)

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
				return ("arms.up", [l_pitch_offset, l_roll_offset])

		return None


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
