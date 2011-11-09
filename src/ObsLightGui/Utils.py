#
# Copyright 2011, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 28 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide.QtGui import QMessageBox, QProgressDialog

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


class ProgressRunnable(QRunnable, QObject):
    '''
    QRunnable implementation which can update a QProgressDialog, and
    send exceptions to a callback.
    '''
    __progressDialog = None
    __isInfinite = False
    # Create two signals: one with no parameter, the other with one integer parameter
    __finished = Signal((), (int, ))
    finished = Signal()
    finishedWithException = Signal(BaseException)

    def __init__(self, func, *args, **kwargs):
        '''
        Initialize the ProgressRunnable with the function to run in thread
        and its optional arguments.
        '''
        QRunnable.__init__(self)
        QObject.__init__(self)
        self.func = func
        self.params = args
        self.kwargs = kwargs

    def setProgressDialog(self, dialog):
        '''
        Set the QProgressDialog (or QProgressBar) to update when finished
        running the function.
        If it is an infinite progress dialog (minimum == maximum),
        the ProgressRunnable will call reset().
        If it is a regular progress dialog (minimum < maximum),
        the ProgressRunnable will increment its value().
        '''
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
        caughtException = None
        try:
            self.func(*self.params, **self.kwargs)
        except BaseException as e:
            caughtException = e
        finally:
            self.__updateValue()
            if caughtException is not None:
                self.finishedWithException.emit(e)
            self.finished.emit()

def detachWithProgress(title, minDuration=500):
    '''
    Decorator which will make a function run in a QThreadPool while
    displaying an infinite QProgressDialog.
    '''
    def showProgress1(func):
        def showProgress2(*args):
            progress = QProgressDialog()
            progress.setLabelText(title)
            progress.setMinimumDuration(minDuration)
            progress.setWindowModality(Qt.WindowModal)
            progress.setRange(0, 0)
            runnable = ProgressRunnable(func, *args)
            runnable.setProgressDialog(progress)
            progress.show()
            QThreadPool.globalInstance().start(runnable)
        return showProgress2
    return showProgress1


# Attempt to write a "run on UI thread" function.
# Does not work because of an obscure threading bug that I did not
# manage to solve.

#class UiThreadRunner(QObject):
#    
#    class FuncParam(object):
#        func = None
#        args = None
#        
#    __runSignal = Signal(FuncParam)
#    
#    def __init__(self):
#        QObject.__init__(self)
#        self.__runSignal.connect(self.__runInUiThread)
#
#    def __runInUiThread(self, funcParam):
#        print "in __runInUiThread(), thread %s" % currentThread()
#        print funcParam.args
#        funcParam.func(*funcParam.args)
#
#    def run(self, func, *args):
#        print "in run(), thread %s" % currentThread()
#        param = UiThreadRunner.FuncParam()
#        param.func = func
#        param.args = args
#        self.__runSignal.emit(param)
#
#uiThreadRunner = UiThreadRunner()
#
#def runInUiThread(func, *args):
#    uiThreadRunner.run(func, *args)


def popupOnException(f):
    '''
    Decorator to catch the exceptions a function may return and display them
    in a warning QMessageBox.
    To be used only in UI thread.
    '''
    def catchException(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except ObsLightErr.OBSLightBaseError as e:
            #runInUiThread(QMessageBox.warning, None, "Exception occurred", e.msg)
            QMessageBox.warning(None, "Exception occurred", e.msg)
        except BaseException as e:
            QMessageBox.critical(None, "Exception occurred", str(e))
    return catchException
