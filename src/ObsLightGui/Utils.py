'''
Created on 28 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QRunnable

class QRunnableImpl(QRunnable):
    '''
    Empty QRunnable implementation.
    PySide's `QRunnable` maps to Qt's C++ QRunnable abstract class, so we can't
    instantiate it first and then replace its "run" method.
    This class provides an implementation which does nothing.
    '''
    def run(self):
        pass
