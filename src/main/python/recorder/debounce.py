'''
Created on 4 Aug 2013

@author: davesnowdon
'''

from threading import Timer


class Debounce(object):
    '''
    Class used to debounce a binary signal
    '''

    def __init__(self, pressed, released, press_delay=0.2, release_delay=0.4):
        self.press_callback = pressed
        self.press_delay = press_delay
        self.release_callback = released
        self.release_delay = release_delay
        self.timer = None
        self.debounced_state = None
        self.last_raw_state = None

    def trigger(self, dataName, value, ignored=None):
        # print "trigger {} -> {}".format(self.last_raw_state, value)
        self.last_raw_state = value
        if self.debounced_state != value:
            if not self.timer:
                self.set_timer(self.delay_for_state(value))

    def _timer_callback(self):
        '''
        raw callback called by timer
        '''

        if self.debounced_state != self.last_raw_state:
            # print "change {} -> {}".format(self.debounced_state, self.last_raw_state)
            self.debounced_state = self.last_raw_state
            if self.debounced_state:
                # print "press"
                self.press_callback()
            else:
                # print "release"
                self.release_callback()

        else:
            # print "no change {}".format(self.debounced_state)
            pass
        # reset, so we can call the timer again
        self.timer = None

    def delay_for_state(self, state):
        if state:
            return self.press_delay
        else:
            return self.release_delay

    def set_timer(self, delay):
        # print "set timer {}".format(delay)
        self.timer = Timer(delay, self._timer_callback)
        self.timer.start()

    def cancel_timer(self):
        if self.timer:
            self.timer.cancel()
