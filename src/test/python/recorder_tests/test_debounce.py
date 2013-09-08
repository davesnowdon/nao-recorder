'''
Created on 4 Aug 2013

@author: dns
'''
import unittest
import types
import time

from recorder.debounce import Debounce

class DebounceTarget(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.press_called = False
        self.release_called = False

    def press_callback(self):
        self.press_called = True

    def release_callback(self):
        self.release_called = True


def null_method(ignored1=None, ignored2=None):
    pass

def make_patched_debounce(target):
    '''
    Make a Debounce instance but patch it so it does not create timer threads
    '''
    debouncer = Debounce(target.press_callback, target.release_callback)
    debouncer.set_timer = types.MethodType(null_method, debouncer)
    return debouncer

class TestDebounce(unittest.TestCase):
    def test_simple_press(self):
        target = DebounceTarget()
        debouncer = make_patched_debounce(target)
        # simulate press
        debouncer.trigger("dummy", 1, "ignored")
        # simulate timer firing
        debouncer._timer_callback()
        # assert that press callback fired
        self.assertTrue(target.press_called, "debounce should have signalled press")

    def test_simple_release(self):
        target = DebounceTarget()
        debouncer = make_patched_debounce(target)
        # simulate press
        debouncer.trigger("dummy", 0, "ignored")
        # simulate timer firing
        debouncer._timer_callback()
        # assert that press callback fired
        self.assertTrue(target.release_called, "debounce should have signalled release")

    def test_press_and_hold_with_noise(self):
        target = DebounceTarget()
        debouncer = make_patched_debounce(target)
        # simulate press
        debouncer.trigger("dummy", 1, "ignored")
        # simulate timer firing
        debouncer._timer_callback()
        # assert that press callback fired
        self.assertTrue(target.press_called, "debounce should have signalled press")
        target.reset()
        debouncer.trigger("dummy", 0, "ignored")
        debouncer.trigger("dummy", 1, "ignored")
        self.assertFalse(target.press_called, "spike should not have triggered new press")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
