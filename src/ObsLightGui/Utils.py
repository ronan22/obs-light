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
from ObsLight.ObsLightTools import isNonEmptyString

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
    send exceptions to a callback. You must implement the run() method,
    or call setRunMethod() with a method to run as first parameter.
    If you implement run() yourself, don't forget to call hasFinished()
    at the end.
    '''
    __progressDialog = None
    __isFinite = False
    __askedToCancel = False

    __started = Signal()
    __progressed = Signal((), (int,))
    __finished = Signal(())
    __sentMessage = Signal((unicode))

    finished = Signal((), (object,))
    caughtException = Signal(BaseException)

    def __init__(self, progressDialog=None):
        '''
        Initialize the ProgressRunnable. Don't forget to call
        ProgressRunnable.__init__(self) when you override.
        It is possible to pass a QProgressDialog as parameter
        (equivalent to call setProgressDialog() after instantiation.
        '''
        QRunnable.__init__(self)
        QObject.__init__(self)
        if progressDialog is not None:
            self.setProgressDialog(progressDialog)

    def cancel(self):
        '''
        Ask the ProgressRunnable to cancel.
        This method is internally connected to the ProgressDialog
        (if there is one) 'canceled' signal.
        '''
        self.__askedToCancel = True
        self.setDialogMessage("Canceled. Waiting for current task to finish...")

    def setProgressDialog(self, dialog):
        '''
        Set the QProgressDialog (or QProgressBar) to update when calling
        hasProgressed() and hasFinished(). You can pass None.
        '''
        # If there was a previous progress dialog, disconnect it.
        if (self.__progressDialog is not None and
            isinstance(self.__progressDialog, QProgressDialog)):
            try:
                self.__progressDialog.canceled.disconnect(self.cancel)
            except BaseException:
                pass
        self.__progressDialog = dialog
        if self.__progressDialog is not None:
            self.__isFinite = self.__progressDialog.minimum() < self.__progressDialog.maximum()
            if isinstance(self.__progressDialog, QProgressDialog):
                # Disconnect its canceled signal from its cancel method
                # so it won't close before cancellation is effective.
                try:
                    self.__progressDialog.canceled.disconnect(self.__progressDialog.cancel)
                except BaseException:
                    pass
                self.__progressDialog.canceled.connect(self.cancel)

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

    def hasStarted(self):
        '''
        Inform the progress dialog that the run method has started.
        (calls its show() method).
        '''
        if self.__progressDialog is not None:
            self.__started.connect(self.__progressDialog.show)
            self.__started.emit()
            self.__started.connect(self.__progressDialog.show)

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
            self.__progressed.connect(self.__progressDialog.show)
            self.__progressed.emit()
            self.__progressed.disconnect(self.__progressDialog.show)

    def hasFinished(self, result=None):
        '''
        Inform the progress dialog that the run method has finished
        its execution (so it will be hidden). Also emits the finished
        signal.
        '''

        if self.__progressDialog is not None:
            if isinstance(self.__progressDialog, QProgressDialog):
                try:
                    self.__progressDialog.canceled.disconnect(self.cancel)
                except BaseException:
                    pass
            self.__finished.connect(self.__progressDialog.reset)
            self.__finished.emit()
            self.__finished.disconnect(self.__progressDialog.reset)
        self.finished.emit()
        self.finished[object].emit(result)

    def hasCaughtException(self, exception):
        '''
        Emits the caughtException signal with exception as parameter.
        '''
        self.caughtException.emit(exception)

    def setDialogMessage(self, message):
        '''
        Set the message displayed in the progress dialog.
        '''
        if self.__progressDialog is not None:
            self.__sentMessage.connect(self.__progressDialog.setLabelText)
            if not isinstance(message, unicode):
                message = unicode(message, errors='replace')
            self.__sentMessage.emit(message)
            self.__sentMessage.disconnect(self.__progressDialog.setLabelText)

    def wasAskedToCancel(self):
        '''
        Returns True if the ProgressRunnable was asked to cancel, using
        its cancel() method.
        '''
        return self.__askedToCancel

    def setRunMethod(self, method, *args, **kwargs):
        '''
        Replace the 'run' method of this instance by one which will
        run 'method' with arguments 'args' and 'kwargs' (expanded),
        and will emit caughtException signal if an exception is caught.
        '''
        def run():
            result = None
            caughtException = None
            try:
                self.hasStarted()
                result = method(*args, **kwargs)
            except BaseException as e:
                caughtException = e
            finally:
                if caughtException is not None:
                    self.hasCaughtException(caughtException)
                self.hasFinished(result)
        self.run = run

    def setFunctionToMap(self, function, iterable, message=None, *otherArgs, **kwargs):
        '''
        Replace the 'run' method of this instance by one which will
        map 'function' on every element of 'iterable'. It is possible to
        change the progress dialog message with 'message' ("%(arg)s" is
        replaced by an unicode representation of the current element),
        and to pass other parameters to the function.
        '''
        def run():
            results = list()

            try:
                self.setMax(len(iterable))
                self.hasStarted()
                for arg in iterable:
                    caughtException = None
                    try:
                        if isNonEmptyString(message):
                            unicodeArg = unicode(arg)
                            self.setDialogMessage(message % {"arg":unicodeArg})
                        results.append(function(arg, *otherArgs, **kwargs))
                    except BaseException as e:
                        caughtException = e
                    finally:
                        if caughtException is not None:
                            self.hasCaughtException(caughtException)
                        self.hasProgressed()
            finally:
                self.hasFinished(results)
        self.run = run


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
        try:
            message = unicode(exception)
        except UnicodeError:
            message = unicode(str(exception), errors="replace")
        QMessageBox.critical(parent, u"Exception occurred", message)

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
