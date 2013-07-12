'''
Created on Dec 31, 2012

@author: dns
'''

import math

from mathutil import FLOAT_CMP_ACCURACY, feq

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


def joints_to_degrees(joints, round_values=True):
    djoints = {}
    if round_values:
        for j, v in joints.iteritems():
            djoints[j] = round(math.degrees(v))
    else:
        for j, v in joints.iteritems():
            djoints[j] = math.degrees(v)
    return djoints

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
        
    def get_joint_angles(self, use_radians=True):
        angles = self.env.motion.getAngles("Body", self.useSensors)
        for n, v in zip(JOINT_NAMES, angles):
            self.joints[n] = v
            
        if use_radians:
            return self.joints
        else:
            return joints_to_degrees(self.joints, True)

    def joint_changes(self, oldangles, newangles, threshold=FLOAT_CMP_ACCURACY):
        """
        Returns a dict containing the changes in angles. Angles that have not changed have their
        values set to None. Requires that oldangles and newangles have the same set
        of keys.
        """
        deltas =  {}
        for k in oldangles:
            j1 = oldangles[k]
            j2 = newangles[k]
            if not feq(j1, j2):
                deltas[k] = j2 - j1
            else:
                deltas[k] = None
        return deltas
    