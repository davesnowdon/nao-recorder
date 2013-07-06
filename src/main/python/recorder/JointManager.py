'''
Created on Dec 31, 2012

@author: dns
'''

import time
from threading import Timer


# joint names in same order as returned by ALMotion.getAngles('Body')
JOINT_NAMES = ('HeadYaw', 'HeadPitch', 
               'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 
               'LWristYaw', 'LHand',
               'LHipYawPitch', 'LHipRoll', 'LHipPitch', 
               'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
               'RHipYawPitch', 'RHipRoll', 'RHipPitch', 
               'RKneePitch',  'RAnklePitch', 'RAnkleRoll',
               'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 
               'RWristYaw', 'RHand')

class Joint(object):
    def __init__(self, name=''):
        super(Joint, self).__init__()
        self._name = name
        self._angle = 0

    @property
    def name(self):
        return self._name

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if self._angle != value:
            self._angle = value
            self.notify()

def do_update(manager, interval):
    nextTime = time.time() + interval
    # run again if requested
    if manager.get_joint_angles():
        delay = nextTime - time.time()
        if delay < 0.0:
            delay = interval
        Timer(delay, do_update, (manager, interval)).start()

class JointManager(object):
    def __init__(self, proxy, interval, useSensors=True):
        self.motionProxy = proxy
        self.interval = interval
        self.useSensors = useSensors
        self.running = True
        self.joints = { }
        for j in JOINT_NAMES:
            self.joints[j] = Joint(j)

    def start(self):
        do_update(self, self.interval)
    
    def stop(self):
        self.running = False
    
    def get_joint(self, name):
        return self.joints[name]
        
    def get_joint_angles(self):
        angles = self.motionProxy.getAngles("Body", self.useSensors)
        for n, v in zip(JOINT_NAMES, angles):
            self.joints[n].angle = v
        return self.running
