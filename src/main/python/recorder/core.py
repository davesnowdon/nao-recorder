'''
Created on 6 Jul 2013

@author: davesnowdon
'''

import collections

import naoutil.naoenv as naoenv
from naoutil import broker
from naoutil import memory
import fluentnao.nao as nao

from JointManager import JointManager
from translators.fluentnao.core import FluentNaoTranslator

RobotConnection = collections.namedtuple('RobotConnection',
                                    ['env', 'broker', 'nao', 'joint_manager', 'event_handlers'])

DEFAULT_TRANSLATOR = FluentNaoTranslator


def get_translator(name=None):
    return DEFAULT_TRANSLATOR()

def robot_connect(hostname, portnumber, event_handlers=None, vocabulary=None):
    broker = broker.Broker('NaoRecorder', naoIp=hostname, naoPort=portnumber)
    if (broker):
        env = naoenv.make_environment(None)
        joint_manager = JointManager(env)
        nao = nao.Nao(env, None)
        do_subscribe(event_handlers)
        if event_handlers and vocabulary:
            env.speechRecognition.setWordListAsVocabulary(vocabulary, False)
        return RobotConnection(env, broker, nao, joint_manager, event_handlers)
    else:
        return None

def robot_disconnect(connection):
    do_unsubscribe(connection.event_handlers)
    connection.broker.shutdown()

def do_subscribe(event_handlers):
    if event_handlers:
        for (key, value) in event_handlers.iteritems():
            memory.subscribeToEvent(key, value)

def do_unsubscribe(event_handlers):
    if event_handlers:
        for key in event_handlers.keys():
            memory.unsubscribeToEvent(key)