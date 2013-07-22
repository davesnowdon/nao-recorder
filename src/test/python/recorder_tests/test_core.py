'''
Created on 15 Jul 2013

@author: davesnowdon
'''

import random
import unittest

from recorder.core import joint_changes
from testutil import POSITION_ZERO, make_random_joints, make_joint_dict

class TestJointChanges(unittest.TestCase):

    def test_no_old_angles(self):
        curAngles = make_joint_dict(POSITION_ZERO)
        changed_joints = joint_changes(None, curAngles)
        print "changed_joints = {}".format(changed_joints)
        self.assertIsNotNone(changed_joints,
                             "joint_changes() should return a set")
        self.assertEqual(len(changed_joints), len(curAngles.values()),
                         "All joint angles should be marked changed")

    def test_no_changed_joints(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j2 = make_joint_dict(POSITION_ZERO)
        changed_joints = joint_changes(j1, j2)
        print "changed_joints = {}".format(changed_joints)
        self.assertIsNotNone(changed_joints,
                             "joint_changes() should return a set")
        self.assertEqual(len(changed_joints), 0,
                         "No joint angles should have changed")

    def test_all_joints_changed(self):
        j1 = make_random_joints()
        j2 = make_random_joints()
        changed_joints = joint_changes(j1, j2)
        self.assertIsNotNone(changed_joints,
                             "joint_changes() should return a set")
        self.assertEqual(len(changed_joints), len(j1.values()),
                         "Length of changed_joints should be same as input values")

    def test_one_joint_changed(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j1['HeadYaw'] = random.random()
        j2 = make_joint_dict(POSITION_ZERO)
        j2['HeadYaw'] = random.random()
        changed_joints = joint_changes(j1, j2)
        print "changed_joints = {}".format(changed_joints)
        self.assertIsNotNone(changed_joints,
                             "joint_changes() should return a set")
        self.assertEqual(len(changed_joints), 1,
                         "Only HeadYaw should have changed")

    def test_two_joints_changed(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j1['LShoulderPitch'] = random.random()
        j1['RHipRoll'] = random.random()
        j2 = make_joint_dict(POSITION_ZERO)
        j2['LShoulderPitch'] = random.random()
        j2['RHipRoll'] = random.random()
        changed_joints = joint_changes(j1, j2)
        print "changed_joints = {}".format(changed_joints)
        self.assertIsNotNone(changed_joints,
                             "joint_changes() should return a set")
        self.assertEqual(len(changed_joints), 2,
                         "Only LShoulderPitch and RHipRoll should have changed")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
