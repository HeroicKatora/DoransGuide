'''
Created on 31.08.2015

@author: Mareas
'''
import os
from threading import Lock
from collections import defaultdict

class FileGuard():
    def __init__(self):
        self.guards = defaultdict(Lock)
    
    def fileLock(self, completePath):
        return self.guards[os.path.abspath(completePath)]