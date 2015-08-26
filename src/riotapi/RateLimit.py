'''
Created on 26.08.2015

@author: Katora
'''
from threading import Lock
import time

class RateLimit():
    '''
    This class restricts the number of api queries in a short time frame to a certain amount thus avoiding unecessary error messages and annoying error handling.
    It is not thread safe, which should not be a problem since we only have one downloading thread anyways.
    '''
    def __init__(self, maxrate, seconds):
        self.maxrate = maxrate
        self.rate = maxrate
        self.minseconds = seconds
        self.seconds = seconds
        self.timestamps = []
        self.lock = Lock()
    
    def __enter__(self):
        self.lock.acquire()
    
    def __exit__(self, type_t, value, traceback):
        self.lock.release()
    
    def reset(self):
        self.timestamps.clear()

    '''
    This method should be called whenever someone tries to access the protected resource
    It blocks when too many callers tried to access in same timeframe.
    Every time it increases the rate by one up to the max rate (linear growth)
    '''
    def inc(self):
        with self:
            while len(self.timestamps) >= self.rate:    #Try to remove an older timestamp
                if (self.timestamps[0]+self.seconds > time.time()):
                    time.sleep(self.timestamps[0]+self.seconds-time.time())
                self.timestamps.pop(0)
            self.timestamps.append(time.time())
            self.rate = min(self.rate+1, self.maxrate)

    '''
    This method decreases the rate limit according to the parameters for a while.
    It also cuts the maxrate in half
    '''
    def dec(self, waitTime):
        with self:
            self.timestamps[0] = min(time.time()+waitTime, self.timestamps[0])
            self.rate = min(self.rate//2, 1)
        
    def cancel(self):
        pass
