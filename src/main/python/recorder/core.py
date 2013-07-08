'''
Created on 6 Jul 2013

@author: davesnowdon
'''

from translators.fluentnao.core import FluentNaoTranslator

DEFAULT_TRANSLATOR = FluentNaoTranslator

def get_translator(name=None):
    return DEFAULT_TRANSLATOR()

