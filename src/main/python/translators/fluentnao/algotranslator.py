
'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import math

class AlgoTranslator(object):
	def __init__(self):
		# command: (desired deg, max deg, min deg)
		self.commands_dict = {
			"arms.forward": {
				'LShoulderPitch': (0, 45, -45),
				'LShoulderRoll': (0, 45, -90),
				'RShoulderPitch': (0, 45, -45),
				'RShoulderRoll': (0, 90, -45)
			},
			"arms.left_forward": {
				'LShoulderPitch': (0, 45, -45),
				'LShoulderRoll': (0, 45, -90)
			},
			"arms.right_forward": {
				'RShoulderPitch': (0, 45, -45),
				'RShoulderRoll': (0, 90, -45)
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
					offset = self.caculate_offset(deg_desired, deg_nao, joint)

					# assign to cmd tuple
					self.assign_offset(joint, cmd_tuple, offset)

				# not in range?
				else:
					range_match = False

			# use command
			if range_match:
				commands.append(cmd_tuple)

		# return all commands needed for arms
		return self.reduce_commands(commands)

	def reduce_commands(self, commands):

		reduced_commands = []
    
    	
		for command_tuple in commands:

			# match end of command
			match = command_tuple[0].split('_')[-1]

			# against collection
			tuples = [c for c in commands if match in c[0]]
			
			if len(tuples) > 1:

				# reduce
				pass

		return commands


	def assign_offset(self, joint, cmd_tuple, offset):

		# Roll?
		if (joint.find('Roll') > -1):
			
			# first offset
			cmd_tuple[1][1] = offset

		else:

			# second offset
			cmd_tuple[1][0] = offset


	def caculate_offset(self, deg_desired, deg_nao, joint):

		# Roll?
		if (joint.find('Roll') > -1):
			
			# Left?
			if (joint.startswith('L')):
				return deg_desired + deg_nao

		# default offset calculation
		return deg_desired - deg_nao