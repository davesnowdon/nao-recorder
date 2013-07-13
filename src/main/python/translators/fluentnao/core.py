'''
Created on 6 Jul 2013

@author: davesnowdon
'''
import algo2translator
from algo2translator import Algo2Translator
from drytranslator import DryTranslator

class FluentNaoTranslator(object):

	def detect_command(self, joint_dict):
		return DryTranslator().detect_command(joint_dict)
		#return Algo2Translator().detect_command(joint_dict)

