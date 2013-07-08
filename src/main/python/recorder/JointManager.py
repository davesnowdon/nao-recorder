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


class JointManager(object):
    def __init__(self, env, useSensors=True):
        self.env = env
        self.useSensors = useSensors
        
        # init dictionary
        self.joints = { }
        for j in JOINT_NAMES:
            self.joints[j] = 0
  
    def get_joint(self, name):
        return self.joints[name]
        
    def get_joint_angles(self):
        angles = self.env.motion.getAngles("Body", self.useSensors)
        for n, v in zip(JOINT_NAMES, angles):
            self.joints[n] = v
        return self.joints
