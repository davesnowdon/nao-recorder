'''
Created on 2 Aug 2013

@author: davesnowdon
'''

import sys
import time

import naoutil.naoenv as naoenv
from naoutil import broker
from naoutil import memory



events = []

def callback(dataName, value, message):
    global events
    t = (time.time(), value)
    events.append(t)

def print_events(dataName=None, value=None, message=None):
    global events
    for e in events:
        print "{t} : {v}".format(t=e[0], v=e[1])

def main(hostname, portnumber):
    print "Connecting to {}:{}".format(hostname, portnumber)
    b = broker.Broker('NaoRecorder', naoIp=hostname, naoPort=portnumber)
    if b:
        env = naoenv.make_environment(None)
        memory.subscribeToEvent("HandLeftBackTouched", callback)
        memory.subscribeToEvent("FrontTactilTouched", print_events)
        print "waiting for events\n"
        time.sleep(120)
        print_events()
        print "done\n"


if __name__ == '__main__':
    if 3 != len(sys.argv):
        main("192.168.0.43", 9559)
    else:
        main(sys.argv[1], int(sys.argv[2]))