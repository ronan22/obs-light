'''
Created on 28 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QRunnable, Signal
from PySide.QtGui import QMessageBox

from ObsLight import ObsLightErr

class QRunnableImpl(QRunnable):
    '''
    Empty QRunnable implementation.
    PySide's `QRunnable` maps to Qt's C++ QRunnable abstract class, so we can't
    instantiate it first and then replace its "run" method.
    This class provides an implementation which does nothing.
    '''
    def run(self):
        pass


class QRunnableImpl2(QRunnable, QObject):
    
    __progressDialog = None
    __isInfinite = False
    # Create a double signal: one with no parameter, the other with one integer parameter
    __finished = Signal((), (int, ))

    
    def __init__(self, method, *args):
        QRunnable.__init__(self)
        QObject.__init__(self)
        self.method = method
        self.params = args

    def setProgressDialog(self, dialog):
        self.__progressDialog = dialog
        if self.__progressDialog is not None:
            self.__isInfinite = self.__progressDialog.minimum() < self.__progressDialog.maximum()
        
    def __updateValue(self):
        if self.__progressDialog is not None:
            if self.__isInfinite:
                # "Real" progress dialog, so increase value
                self.__finished[int].connect(self.__progressDialog.setValue)
                value = self.__progressDialog.value()
                self.__finished[int].emit(value + 1)
                self.__finished[int].disconnect(self.__progressDialog.setValue)
            else:
                # "Infinite" progress dialog, so reset it
                self.__finished.connect(self.__progressDialog.reset)
                self.__finished.emit()
                self.__finished.disconnect(self.__progressDialog.reset)

    def run(self):
        self.method(*self.params)
        self.__updateValue()

def popupOnException(f):
    def catchException(*args):
        try:
            f(*args)
        except ObsLightErr.OBSLightBaseError as e:
            QMessageBox.warning(None, "Exception occurred", e.msg)
    return catchException
