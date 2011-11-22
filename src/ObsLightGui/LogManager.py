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
Created on 21 nov. 2011

@author: Florent Vennetier
'''

from logging import Handler
from logging import Formatter

from PySide.QtCore import QObject, Signal
from PySide.QtGui import QPlainTextEdit

from ObsLight import ObsLightConfig

class LogManager(QObject):
    '''
    
    '''

    class MyHandler(Handler):

        reEmit = None

        def __init__(self, reEmitMethod):
            Handler.__init__(self)
            self.reEmit = reEmitMethod

        def emit(self, record):
            self.reEmit(record)


    __gui = None
    __logDialog = None
    __logTextEdit = None
    __myHandler = None

    appendMessage = Signal(unicode)

    def __init__(self, gui):
        '''
        
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__logDialog = self.__gui.loadWindow(u"obsLightLog.ui")
        self.__logTextEdit = self.__logDialog.findChild(QPlainTextEdit, u"logTextEdit")
        self.connectLogger()

    def connectLogger(self):
        #self.appendMessage.connect(self.__logTextEdit.appendPlainText)
        self.appendMessage.connect(self.__logTextEdit.appendHtml)
        self.__myHandler = LogManager.MyHandler(self.emitRecord)
        #formatter = Formatter(u"%(asctime)s <font color=\"#0000FF\">%(name)s</font>: %(message)s")
        formatter = Formatter(ObsLightConfig.getObsLightGuiFormatterString())
        self.__myHandler.setFormatter(formatter)
        self.__gui.getObsLightManager().addLoggerHandler(self.__myHandler)

    def disconnectLogger(self):
        #self.appendMessage.disconnect(self.__logTextEdit.appendPlainText)
        self.appendMessage.disconnect(self.__logTextEdit.appendHtml)
        self.__gui.getObsLightManager().removeLoggerHandler(self.__myHandler)

    def emitRecord(self, record):
        formatted = self.__myHandler.format(record)
        try:
            if isinstance(formatted, unicode):
                self.appendMessage.emit(formatted)
            else:
                self.appendMessage.emit(unicode(formatted, errors='replace'))
        except BaseException:
            self.__myHandler.handleError(record)

    def show(self):
        self.__logDialog.show()
        self.__logDialog.activateWindow()
