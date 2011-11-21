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
Created on 27 sept. 2011

@author: Florent Vennetier
'''

import sys
from os.path import dirname, join

from PySide.QtCore import QIODevice, QFile, QMetaObject, QObject, Qt, Signal
from PySide.QtGui import QApplication, QProgressDialog, QStatusBar
from PySide.QtUiTools import QUiLoader

from ObsLight.ObsLightErr import OBSLightBaseError

from ProjectManager import ProjectManager
from ActionManager import MainWindowActionManager
from LogManager import LogManager
from Utils import exceptionToMessageBox

class Gui(QObject):
    '''
    ObsLight GUI main class. Keeps reference to the main window
    and to the ObsLightManager.
    '''
    application = None
    uiLoader = None
    __mainWindow = None
    __statusBar = None
    __obsLightManager = None
    __obsProjectManager = None
    __logManager = None
    __mainWindowActionManager = None
    __progress = None

    __messageSignal = Signal((str, int))

    def __init__(self, obsLightManager=None):
        QObject.__init__(self)
        self.application = QApplication(sys.argv)
        self.uiLoader = QUiLoader()
        self.__obsLightManager = obsLightManager

    def loadWindow(self, uiFile):
        '''
        Load a Window from UI file.
        '''
        path = join(dirname(__file__), u"ui", uiFile)
        windowFile = QFile(path)
        windowFile.open(QIODevice.ReadOnly | QIODevice.Text)
        # Make all loaded windows children of mainWindow, except mainWindow itself
        window = self.uiLoader.load(windowFile, self.__mainWindow)
        windowFile.close()
        QMetaObject.connectSlotsByName(window)
        return window

    def __loadMainWindow(self):
        self.__mainWindow = self.loadWindow(u"obsLightMain.ui")
        self.__mainWindowActionManager = MainWindowActionManager(self)
        self.__statusBar = self.__mainWindow.findChild(QStatusBar, u"mainStatusBar")
        self.__messageSignal.connect(self.__statusBar.showMessage)
        self.__mainWindow.show()

    def __createProgressDialog(self):
        self.__progress = QProgressDialog(self.__mainWindow)
        self.__progress.setMinimumDuration(500)
        self.__progress.setWindowModality(Qt.WindowModal)
        self.__progress.setCancelButton(None)
        # make the progress "infinite"
        self.__progress.setRange(0, 0)

    def getMainWindow(self):
        '''
        Returns the main window object (may be None).
        '''
        return self.__mainWindow

    def getProgressDialog(self):
        '''
        Get the main QProgressDialog. It is window-modal, has no cancel
        button and is infinite.
        '''
        if self.__progress is None:
            self.__createProgressDialog()
        return self.__progress

    def getObsLightManager(self):
        '''
        Get the unique ObsLightManager instance.
        '''
        return self.__obsLightManager

    def getLogManager(self):
        if self.__logManager is None:
            self.__logManager = LogManager(self)
        return self.__logManager

    def statusBarErrorCallback(self, error):
        '''
        Display errors in the status bar of the main window.
        '''
        if isinstance(error, OBSLightBaseError):
            self.sendStatusBarMessage(u"OBS Light error: %s" % error.msg, 30000)
        else:
            self.sendStatusBarMessage(u"Caught exception: %s" % str(error), 30000)

    def popupErrorCallback(self, error):
        '''
        Display errors in a popup. Must be called from UI thread, or
        with a Qt signal.
        '''
        exceptionToMessageBox(error, self.__mainWindow)

    def sendStatusBarMessage(self, message, timeout=0):
        '''
        Display a message in the status bar of the main window.
        Timeout is in milliseconds.
        '''
        self.__messageSignal.emit(message, timeout)

    def main(self):
        self.__loadMainWindow()
        self.__obsProjectManager = ProjectManager(self)
        return self.application.exec_()


if __name__ == '__main__':
    gui = Gui()
    gui.main()
