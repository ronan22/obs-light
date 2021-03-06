#
# Copyright 2011-2012, Intel Inc.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Created on 28 oct. 2011

@author: Florent Vennetier
"""

import sys
import traceback
from time import sleep

from PySide.QtCore import QObject, QRegExp, QRunnable, QThreadPool, Signal
from PySide.QtGui import QApplication, QColor, QGraphicsColorizeEffect
from PySide.QtGui import QMessageBox, QDialog

from ObsLight import ObsLightErr
from ObsLight.ObsLightUtils import isNonEmptyString
from ObsLight.ObsLightTools import dumpError

from ObsLight import ObsLightConfig

URL_REGEXP = QRegExp(u"http[s]?://.+")
SERVER_ALIAS_REGEXP = QRegExp(u"[^\\s:;,/]+")
PROJECT_ALIAS_REGEXP = QRegExp(u"[^\\s:;,/]+")
PATCH_NAME_REGEXP = QRegExp(u"\\S+\.patch")
PACKAGE_NAME_REGEXP = QRegExp(u"[^\\s:;,/]+")

class ProgressRunnable2(QObject, QRunnable):
    """
    QRunnable implementation which can update a QProgressDialog, and
    emit signals when it has finished or caught exceptions.
    You can implement the `ProgressRunnable2.run()` method, or call
    `ProgressRunnable2.setRunMethod()` or
    `ProgressRunnable2.setFunctionToMap()` with a function to run as
    first parameter. If you implement `ProgressRunnable2.run()`
    yourself, don't forget to call `ProgressRunnable2.setHasStarted`
    at the beginning, `ProgressRunnable2.setHasFinished()`
    at the end (and eventually `ProgressRunnable2.setHasProgressed()`
    in the middle).
    
    `ProgressRunnable2.finished[object]` and `ProgressRunnable2.finished`
    signals are emitted after `ProgressRunnable2.setHasFinished()`
    has been called (either by your method or by the one automatically
    generated), the first with the result of the
    `ProgressRunnable2.run()` method as parameter (eventually None),
    the second without parameter.
    
    `ProgressRunnable2.caughtException` signal is emitted after
    `ProgressRunnable2.setHasCaughtException()` method has been called.
    It is called by the automatically generated run methods when they
    catch an exception (it may happen several time if the run method
    has been generated by `ProgressRunnable2.setFunctionToMap()`.
    """


    # Create a single signal, without parameter
    __started = Signal(())
    # Create two signals: one without parameter, the other with one integer parameter
    # The only documentation I found about this syntax is here:
    #   http://qt-project.org/wiki/Signals_and_Slots_in_PySide
    __progressed = Signal((), (int,))
    __finished = Signal(())
    __sentMessage = Signal((unicode))

    finished = Signal((), (object,))
    caughtException = Signal((BaseException))

    def __init__(self, progressDialog=None):
        """
        Initialize the ProgressRunnable. Don't forget to call
        ProgressRunnable.__init__(self) when you override.
        It is possible to pass a QProgressDialog as parameter
        (equivalent to call setProgressDialog() after instantiation.
        """
        QObject.__init__(self)
        QRunnable.__init__(self)

        self.result = None

        self.__finishedCalled = False
        self.__startedCalled = False
        self.__progressDialog = None
        self.__isFinite = False
        self.__askedToCancel = False
        self.__hasCaughtException = False

        self.destroyed.connect(self.__onDestroy)

        if progressDialog is not None:
            self.setProgressDialog(progressDialog)

    def __onDestroy(self):
        # Seems like disconnections are done automatically
        # and doing it a second time crashes the program.
#        if self.__progressDialog is not None:
#            self.__disconnectProgress()
        pass

    def __connectProgress(self):
        if isinstance(self.__progressDialog, QDialog):
            # Disconnect its canceled signal from its cancel method
            # so it won't close before cancellation is effective.
            try:
                self.__progressDialog.canceled.disconnect(self.__progressDialog.cancel)
            except BaseException:
                pass
            # Cancel the ProgressRunnable when user asks
            self.__progressDialog.canceled.connect(self.cancel)

        # Show the progress when starting
        self.__started.connect(self.__progressDialog.show)
        # Update progress value when progressing
        self.__progressed[int].connect(self.__progressDialog.setValue)
        # Reset the progress when finished
        self.__finished.connect(self.__progressDialog.reset)
        # Update label when user asks
        self.__sentMessage.connect(self.__progressDialog.setLabelText)

    def __disconnectProgress(self):
        if isinstance(self.__progressDialog, QDialog):
            try:
                self.__progressDialog.canceled.disconnect(self.__progressDialog.cancel)
            except BaseException as e:
                print e
        self.__started.disconnect(self.__progressDialog.show)
        self.__progressed[int].disconnect(self.__progressDialog.setValue)
        self.__finished.disconnect(self.__progressDialog.reset)
        self.__sentMessage.disconnect(self.__progressDialog.setLabelText)

    def cancel(self):
        """
        Ask the ProgressRunnable to cancel.
        This method is internally connected to the ProgressDialog
        (if there is one) 'canceled' signal.
        """
        self.__askedToCancel = True
        self.setDialogMessage("Canceled. Waiting for current task to finish...")

    def setProgressDialog(self, dialog):
        """
        Set the QProgressDialog (or QProgressBar) to update when calling
        setHasProgressed() and setHasFinished(). You can pass None.
        """
        # If there was a previous progress dialog, disconnect it.
        if (self.__progressDialog is not None):
            self.__disconnectProgress()

        self.__progressDialog = dialog
        if self.__progressDialog is not None:
            self.__isFinite = self.__progressDialog.minimum() < self.__progressDialog.maximum()
            self.__connectProgress()

    def getProgressDialog(self):
        """
        Get the QProgressDialog (or QProgressBar) which has been set using
        setProgressDialog(). Returns None if there is not progress dialog.
        """
        return self.__progressDialog

    def setMax(self, maximum):
        """
        Set the range of the progress dialog from 0 to maximum.
        An infinite progress dialog will be transformed to a finite one.
        """
        if self.__progressDialog is not None:
            self.__progressDialog.setRange(0, maximum)
            self.__isFinite = True

    def setHasStarted(self):
        """
        Inform the progress dialog that the run method has started.
        (calls its show() method).
        """
        if self.__startedCalled:
            raise RuntimeError(u'setHasStarted() called twice')
        self.__startedCalled = True

        if self.__progressDialog is not None:
            self.__started.emit()

    def setHasProgressed(self, howMuch=1):
        """
        Inform the progress dialog that the run method has progressed
        in its execution. The howMuch parameter allows you to progress
        of more than one step at a time.
        """
        if self.__progressDialog is not None:
            if self.__isFinite:
                # "Real" progress dialog, so increase value
                value = self.__progressDialog.value()
                self.__progressed[int].emit(value + howMuch)
            else:
                # "Infinite" progress dialog, so do nothing
                pass

    def setHasFinished(self, result=""):
        """
        Inform the progress dialog that the run method has finished
        its execution (so it will be hidden). Also emits the finished
        signal.
        """
        if result == None:
            result = ""
        if self.__finishedCalled:
            raise RuntimeError(u'setHasFinished() called twice')
        self.result = result
        self.__finishedCalled = True
        if self.__progressDialog is not None:
            if isinstance(self.__progressDialog, QDialog):
                try:
                    self.__progressDialog.canceled.disconnect(self.cancel)
                except BaseException:
                    pass
            self.__finished.emit()
        # We got some crashes after catching exception,
        # especially in wizard when loading project list.
#        if not self.__hasCaughtException:
#            # FIXME: check if "None" can be emitted
        self.finished[object].emit(result)
        self.finished.emit()

    def setHasCaughtException(self, exception):
        """
        Emits the caughtException signal with exception as parameter.
        """
        self.__hasCaughtException = True
        self.caughtException.emit(exception)

    def setDialogMessage(self, message):
        """
        Set the message displayed in the progress dialog.
        """
        if self.__progressDialog is not None:
            if not isinstance(message, unicode):
                message = unicode(message, errors='replace')
            self.__sentMessage.emit(message)

    def wasAskedToCancel(self):
        """
        Returns True if the ProgressRunnable was asked to cancel, using
        its cancel() method.
        """
        return self.__askedToCancel

    def setRunMethod(self, method, *args, **kwargs):
        """
        Replace the 'run' method of this instance by one which will
        run 'method' with arguments 'args' and 'kwargs' (expanded),
        and will emit caughtException signal if an exception is caught.
        """
        def run():
            result = None
            exceptionCaught = None
            try:
                self.setHasStarted()
                result = method(*args, **kwargs)
            except BaseException as e:
                traceback_ = sys.exc_info()[2]
                exceptionCaught = e
                exceptionCaught.traceback = traceback_
            finally:
                if exceptionCaught is not None:
                    self.setHasCaughtException(exceptionCaught)
                self.setHasFinished(result)
                self.deleteLater()
        self.run = run

    def _getisFinite(self):
        return self.__isFinite

    def setFunctionToMap(self, function, iterable, message=None, *otherArgs, **kwargs):
        """
        Replace the 'run' method of this instance by one which will
        map 'function' on every element of 'iterable'. It is possible to
        change the progress dialog message with 'message' ("%(arg)s" is
        replaced by an unicode representation of the current element),
        and to pass other parameters to the function.
        """
        def run():
            results = list()
            try:
                if self._getisFinite():
                    self.setMax(len(iterable))
                self.setHasStarted()
                for arg in iterable:
                    if self.wasAskedToCancel():
                        break
                    caughtException = None
                    try:
                        if isNonEmptyString(message):
                            unicodeArg = unicode(str(arg), errors='replace')
                            self.setDialogMessage(message % {"arg":unicodeArg})
                        results.append(function(arg, *otherArgs, **kwargs))
                    except BaseException as e:
                        traceback_ = sys.exc_info()[2]
                        caughtException = e
                        caughtException.traceback = traceback_
                    finally:
                        if caughtException is not None:
                            self.setHasCaughtException(caughtException)
                        self.setHasProgressed()
            except:
                print sys.exc_info()
            finally:
                self.setHasFinished(results)
                self.deleteLater()
        self.run = run

    def runOnGlobalInstance(self, wait=False):
        """
        Run this ProgressRunnable on the global QThreadPool instance.
        If `wait` is True, process the UI events while waiting for the
        ProgressRunnable to finish.
        """
        QThreadPool.globalInstance().start(self)
        if wait:
            # self.__finishedCalled is made True by the setHasFinished()
            # method, which is called from try/finally blocks so guaranteed
            # to be called even if there are exceptions.
            while not self.__finishedCalled:
                sleep(0.01)
                QApplication.processEvents()

class ProgressRunnable3(ProgressRunnable2):
    def setFunctionToMap(self, function, iterable, message=None, *otherArgs, **kwargs):
        """
        Replace the 'run' method of this instance by one which will
        map 'function' on every element of 'iterable'. It is possible to
        change the progress dialog message with 'message' ("%(arg)s" is
        replaced by an unicode representation of the current element),
        and to pass other parameters to the function.
        """
        def run():
            results = list()
            try:
                if self._getisFinite():
                    self.setMax(len(iterable))
                self.setHasStarted()
                for arg in iterable:
                    if self.wasAskedToCancel():
                        break
                    caughtException = None
                    try:
                        if isNonEmptyString(message):
                            unicodeArg = unicode(str(arg), errors='replace')
                            self.setDialogMessage(message % {"arg":unicodeArg})
                        results.append((arg, function(arg, *otherArgs, **kwargs)))
                    except BaseException as e:
                        traceback_ = sys.exc_info()[2]
                        caughtException = e
                        caughtException.traceback = traceback_
                        results.append((arg, 1))
                    finally:
                        if caughtException is not None:
                            self.setHasCaughtException(caughtException)
                        self.setHasProgressed()
            except:
                print sys.exc_info()
            finally:
                self.setHasFinished(results)
                self.deleteLater()
        self.run = run



QThreadPool.globalInstance().setExpiryTimeout(0)

def firstArgLast(func):
    """
    Return a function which will call 'func' with first argument
    as last argument.
    """
    def swappedArgsFunc(*args, **kwargs):
        newArgs = list(args[1:])
        newArgs.append(args[0])
        return func(*newArgs, **kwargs)
    return swappedArgsFunc

class UiFriendlyTask(object):
    """
    A task that will run a function in a thread while refreshing UI.
    Result is available in `UiFriendlyTask.result` after calling
    `UiFriendlyTask.join()`.
    """

    def __init__(self):
        self.hasFinished = False
        self.result = None
        self.caughtException = None

    def _setHasFinished(self, result1):
        self.result = result1
        self.hasFinished = True

    def _setHasCaughtException(self, theException):
        self.caughtException = theException

    def join(self, delay=0.1):
        """
        Calls `QApplication.processEvents()` every `delay`
        until the task has finished.
        """
        QApplication.processEvents()
        while not self.hasFinished:
            sleep(delay)
            QApplication.processEvents()

    def start(self, func, *args, **kwargs):
        """
        Run `func` with arguments `args` and `kwargs`
        on global thread pool.
        """
        runnable = ProgressRunnable2()
        if "uiFriendlyTask_progressDialog" in kwargs:
            dialog = kwargs.pop("uiFriendlyTask_progressDialog")
            if dialog is not None:
                runnable.setProgressDialog(dialog)
        runnable.setRunMethod(func, *args, **kwargs)
        runnable.finished[object].connect(self._setHasFinished)
        runnable.caughtException.connect(self._setHasCaughtException)
        runnable.runOnGlobalInstance()

def uiFriendly(refreshDelay=0.1):
    """
    Decorator which will make a function run in a QThreadPool while
    processing UI events. Accepts a QProgressDialog instance as
    keyword argument with key "uiFriendlyTask_progressDialog".
    """
    def uiFriendly1(func):
        def uiFriendlyFunc(*args, **kwargs):
            task = UiFriendlyTask()
            task.start(func, *args, **kwargs)
            task.join(refreshDelay)
            if task.caughtException is not None:
                raise task.caughtException
            return task.result
        return uiFriendlyFunc
    return uiFriendly1

def exceptionToMessageBox(exception, parent=None, traceback_=None):
    """
    Display an exception in a QMessageBox.
    OBSLightBaseErrors are displayed as warnings, other types of
    exceptions are displayed as critical.
    To be called only from UI thread.
    """
    if isinstance(exception, ObsLightErr.OBSLightBaseError):
        message = exception.msg
        # Uncomment these lines if you want to display tracebacks
        # with OBS Light exceptions.
#        if traceback_ is not None:
#            message += "\n\n" + "".join(traceback.format_tb(traceback_))
        QMessageBox.warning(parent, "Exception occurred", message)
    else:
        if traceback_ is None and 'traceback' in dir(exception):
            traceback_ = exception.traceback
        try:
            message = unicode(exception)
        except UnicodeError:
            message = unicode(str(exception), errors="replace")
        logPath = dumpError(type(exception), message, traceback_)

        if (ObsLightConfig.getObslightLoggerLevel() == "DEBUG") and (traceback_ is not None):
            message += "\n\n" + "".join(traceback.format_tb(traceback_))
        else:
            message += "\n\nlogPath: " + logPath
        QMessageBox.critical(parent, "Exception occurred", message)

def popupOnException(f):
    """
    Decorator to catch the exceptions a function may return and display them
    in a warning QMessageBox.
    To be used only on methods running in UI thread.
    """
    def catchException(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseException as e:
            traceback_ = sys.exc_info()[2]
            exceptionToMessageBox(e, traceback_=traceback_)
    return catchException

def colorizeWidget(widget, color):
    """
    Set a graphic effect on `widget` using `color`.
    `color` can be a `QtGui.QColor` or an object suitable for
    the constructor of `QtGui.QColor` (such as a color name
    or a long integer).
    """
    effect = QGraphicsColorizeEffect(widget)
    if not isinstance(color, QColor):
        color = QColor(color)
    effect.setColor(color)
    widget.setGraphicsEffect(effect)

def removeEffect(widget):
    """
    Set the graphic effect of `widget` to None.
    """
    widget.setGraphicsEffect(None)

def getSelectedRows(abstractItemView):
    """
    Return a set of indices of the selected rows of `abstractItemView`,
    without duplicates.
    """
    indices = abstractItemView.selectedIndexes()
    if len(indices) < 1:
        indices.append(abstractItemView.currentIndex())
    rows = set()
    for index in indices:
        if index.isValid():
            row = index.row()
            rows.add(row)
    return rows
