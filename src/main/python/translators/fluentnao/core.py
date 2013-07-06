'''
Created on 6 Jul 2013

@author: dns
'''
import math

def detect_command(joint_dict):

	l_should_pitch = math.degrees(joint_dict['LShoulderPitch'])
	l_should_roll = math.degrees(joint_dict['LShoulderRoll'])

	#print 'LShoulderPitch: ' + str(l_should_pitch)
	#print 'LShoulderRoll: ' + str(l_should_roll)

	# match pitch
	if l_should_pitch <= 45 and l_should_pitch >= -45:

		pitch_offset = 0 + l_should_pitch 

		# match roll
		if l_should_roll <= 45:
			roll_offset = 0 + l_should_roll
			return ("arms.left_forward", [pitch_offset, roll_offset]) 

	return None
