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

from PySide.QtCore import QObject, Signal
from PySide.QtGui import QPlainTextEdit

class LogManager(QObject, Handler):
    '''
    
    '''
    __gui = None
    __logDialog = None
    __logTextEdit = None

    __newMessage = Signal((unicode))

    def __init__(self, gui):
        '''
        
        '''
        QObject.__init__(self)
        Handler.__init__(self)
        self.__gui = gui
        self.__logDialog = self.__gui.loadWindow("obsLightLog.ui")
        self.__logTextEdit = self.__logDialog.findChild(QPlainTextEdit, "logTextEdit")
        self.__newMessage.connect(self.__logTextEdit.appendPlainText)

    def emit(self, record):
        if not isinstance(record, unicode):
            record = unicode(record)
        self.__newMessage.emit(record)

    def show(self):
        self.__logDialog.show()
        self.__logDialog.setFocus()
