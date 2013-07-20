'''
Created on 15 Jul 2013

@author: davesnowdon
'''

import random
import unittest

from recorder.core import joint_changes, joints_to_degrees
from testutil import POSITION_ZERO, make_joint_dict, make_random_joints

class TestJointChanges(unittest.TestCase):


    def test_no_changed_joints(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j2 = make_joint_dict(POSITION_ZERO)
        deltas = joint_changes(j1, j2)
        print "deltas = {}".format(deltas)
        self.assertIsNotNone(deltas,
                             "joint_changes() should return a dict")
        nn = filter(lambda x: not x is None, deltas.values())
        print "nn = {}".format(nn)
        self.assertEqual(len(nn), 0,
                         "No joint angles should have changed")

    def test_all_joints_changed(self):
        j1 = make_random_joints()
        j2 = make_random_joints()
        deltas = joint_changes(j1, j2)
        self.assertIsNotNone(deltas,
                             "joint_changes() should return a dict")

        nn = filter(lambda x: not x is None, deltas.values())
        self.assertEqual(len(nn), len(j1.values()),
                         "Length of deltas should be same as input values")

    def test_one_joint_changed(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j1['HeadYaw'] = random.random()
        j2 = make_joint_dict(POSITION_ZERO)
        j2['HeadYaw'] = random.random()
        deltas = joint_changes(j1, j2)
        print "deltas = {}".format(deltas)
        self.assertIsNotNone(deltas,
                             "joint_changes() should return a dict")
        nn = filter(lambda x: not x is None, deltas.values())
        print "nn = {}".format(nn)
        self.assertEqual(len(nn), 1,
                         "Only HeadYaw should have changed")

    def test_two_joints_changed(self):
        # ensure dicts are different objects, but with same values
        j1 = make_joint_dict(POSITION_ZERO)
        j1['LShoulderPitch'] = random.random()
        j1['RHipRoll'] = random.random()
        j2 = make_joint_dict(POSITION_ZERO)
        j2['LShoulderPitch'] = random.random()
        j2['RHipRoll'] = random.random()
        deltas = joint_changes(j1, j2)
        print "deltas = {}".format(deltas)
        self.assertIsNotNone(deltas,
                             "joint_changes() should return a dict")
        nn = filter(lambda x: not x is None, deltas.values())
        print "nn = {}".format(nn)
        self.assertEqual(len(nn), 2,
                         "Only LShoulderPitch and RHipRoll should have changed")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
