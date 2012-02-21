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
'''
Created on 21 nov. 2011

@author: Florent Vennetier
'''

from logging import Handler
from logging import Formatter

from PySide.QtCore import QObject, Signal

from ObsLight import ObsLightConfig
from ObsLightGuiObject import ObsLightGuiObject

class LogManager(QObject, ObsLightGuiObject):
    """
    Manage the printing of logs in a separate window.
    """

    # We cannot implement emit() in LogManager because it has
    # already an emit() method inherited from QObject.
    # So we wrote MyHandler class.
    class MyHandler(Handler):
        """
        A subclass of logging.Handler which forward calls
        to `emit` to the function it got as constructor parameter.
        """

        def __init__(self, reEmitMethod):
            """
            Initialize the handler. `reEmitMethod` should be a function
            taking one logging.LogRecord parameter.
            """
            Handler.__init__(self)
            self.reEmit = reEmitMethod

        def emit(self, record):
            """
            Forward `record` to the function passed as constructor
            parameter.
            """
            self.reEmit(record)


    appendMessage = Signal(unicode)

    def __init__(self, gui):
        """
        Initialise the LogManager. `gui` must be a reference to
        the main `Gui` instance.
        """
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__logDialog = self.gui.loadWindow(u"obsLightLog.ui")
        self.__logTextEdit = self.__logDialog.logTextEdit
        self.__myHandler = None
        self.connectLogger()

    def connectLogger(self):
        """
        Create a MyHandler instance and bind it to the logger of ObsLight.
        """
        self.appendMessage.connect(self.__logTextEdit.appendHtml)
        self.__myHandler = LogManager.MyHandler(self.emitRecord)
        formatter = Formatter(ObsLightConfig.getObsLightGuiFormatterString())
        self.__myHandler.setFormatter(formatter)
        self.manager.addLoggerHandler(self.__myHandler)

    def disconnectLogger(self):
        """
        Unbind the MyHandler instance from the logger of ObsLight.
        """
        self.appendMessage.disconnect(self.__logTextEdit.appendHtml)
        self.manager.removeLoggerHandler(self.__myHandler)

    def emitRecord(self, record):
        """
        Display the content of a logging.LogRecord instance
        in the log window.
        """
        formatted = self.__myHandler.format(record)
        try:
            if isinstance(formatted, unicode):
                message = formatted
            else:
                message = unicode(formatted, errors='replace')
            message = message.replace(u"\n", u"<br />")
            self.appendMessage.emit(message)
        except BaseException:
            self.__myHandler.handleError(record)

    def show(self):
        """
        Display the log window and give it the focus.
        """
        self.__logDialog.show()
        self.__logDialog.activateWindow()

    def close(self):
        """
        Close the log window.
        """
        self.__logDialog.close()
