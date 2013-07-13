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
