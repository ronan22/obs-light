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
    __isFinite = False
    # Create two signals: one with no parameter, the other with one integer parameter
    __finished = Signal((), (int,))
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
            self.__isFinite = self.__progressDialog.minimum() < self.__progressDialog.maximum()

    def __updateValue(self):
        if self.__progressDialog is not None:
            if self.__isFinite:
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


class ProgressRunnable2(QRunnable, QObject):
    '''
    QRunnable implementation which can update a QProgressDialog, and
    send exceptions to a callback. You must implement the run() method.
    '''
    __progressDialog = None
    __isFinite = False

    __progressed = Signal((), (int,))

    finished = Signal()
    caughtException = Signal(BaseException)

    def __init__(self):
        '''
        Initialize the ProgressRunnable. Don't forget to call
        ProgressRunnable.__init__(self) when you override.
        '''
        QRunnable.__init__(self)
        QObject.__init__(self)

    def setProgressDialog(self, dialog):
        '''
        Set the QProgressDialog (or QProgressBar) to update when calling
        hasProgressed() and hasFinished(). You can pass None.
        '''
        self.__progressDialog = dialog
        if self.__progressDialog is not None:
            self.__isFinite = self.__progressDialog.minimum() < self.__progressDialog.maximum()

    def getProgressDialog(self):
        '''
        Get the QProgressDialog (or QProgressBar) which has been set using
        setProgressDialog(). Returns None if there is not progress dialog.
        '''
        return self.__progressDialog

    def setMax(self, maximum):
        '''
        Set the range of the progress dialog from 0 to maximum.
        An infinite progress dialog will be transformed to a finite one.
        '''
        if self.__progressDialog is not None:
            self.__progressDialog.setRange(0, maximum)
            self.__isFinite = True

    def hasProgressed(self, howMuch=1):
        '''
        Inform the progress dialog that the run method has progressed
        in its execution. The howMuch parameter allows you to progress
        of more than one step at a time.
        '''
        if self.__progressDialog is not None:
            if self.__isFinite:
                # "Real" progress dialog, so increase value
                self.__progressed[int].connect(self.__progressDialog.setValue)
                value = self.__progressDialog.value()
                self.__progressed[int].emit(value + howMuch)
                self.__progressed[int].disconnect(self.__progressDialog.setValue)
            else:
                # "Infinite" progress dialog, so do nothing
                pass
            self.__progressDialog.show()

    def hasFinished(self):
        '''
        Inform the progress dialog that the run method has finished
        its execution (so it will be hidden). Also emits the finished
        signal.
        '''
        if self.__progressDialog is not None:
            self.__progressed.connect(self.__progressDialog.reset)
            self.__progressed.emit()
            self.__progressed.disconnect(self.__progressDialog.reset)
        self.finished.emit()

    def hasCaughtException(self, exception):
        '''
        Emits the caughtException signal with exception as parameter.
        '''
        self.caughtException.emit(exception)


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

def exceptionToMessageBox(exception, parent=None):
    '''
    Display an exception in a QMessageBox.
    OBSLightBaseErrors are displayed as warnings, other types of
    exceptions are displayed as critical.
    To be called only from UI thread.
    '''
    if isinstance(exception, ObsLightErr.OBSLightBaseError):
        QMessageBox.warning(parent, u"Exception occurred", exception.msg)
    else:
        QMessageBox.critical(parent, u"Exception occurred", unicode(exception))

def popupOnException(f):
    '''
    Decorator to catch the exceptions a function may return and display them
    in a warning QMessageBox.
    To be used only on methods running in UI thread.
    '''
    def catchException(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except BaseException as e:
            exceptionToMessageBox(e)
    return catchException
