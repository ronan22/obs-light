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
    __infiniteProgress = None
    __progress = None

    __messageSignal = Signal((str, int))

    def __init__(self, obsLightManager=None):
        QObject.__init__(self)
        self.application = QApplication(sys.argv)
        self.application.aboutToQuit.connect(self.__beforeQuitting)
        self.uiLoader = QUiLoader()
        # Need to set working directory in order to load icons
        self.uiLoader.setWorkingDirectory(join(dirname(__file__), u"ui"))
        self.__obsLightManager = obsLightManager
        self.__loadMainWindow()
        self.__obsProjectManager = ProjectManager(self)
        self.__logManager = LogManager(self)

    def __beforeQuitting(self):
        self.__logManager.disconnectLogger()

    def loadWindow(self, uiFile, mainWindowAsParent=True):
        '''
        Load a Window from UI file.
        '''
        path = join(dirname(__file__), u"ui", uiFile)
        windowFile = QFile(path)
        windowFile.open(QIODevice.ReadOnly | QIODevice.Text)
        # Make all loaded windows children of mainWindow, except mainWindow itself
        window = self.uiLoader.load(windowFile, self.__mainWindow if mainWindowAsParent else None)
        windowFile.close()
        QMetaObject.connectSlotsByName(window)
        return window

    def __loadMainWindow(self):
        self.__mainWindow = self.loadWindow(u"obsLightMain.ui")
        self.__mainWindowActionManager = MainWindowActionManager(self)
        self.__statusBar = self.__mainWindow.findChild(QStatusBar, u"mainStatusBar")
        self.__messageSignal.connect(self.__statusBar.showMessage)
        self.__mainWindow.show()

    def __createInfiniteProgressDialog(self):
        self.__infiniteProgress = QProgressDialog(self.__mainWindow)
        self.__infiniteProgress.setMinimumDuration(500)
        self.__infiniteProgress.setWindowModality(Qt.WindowModal)
        self.__infiniteProgress.setCancelButton(None)
        # make the progress "infinite"
        self.__infiniteProgress.setRange(0, 0)
        self.__infiniteProgress.addAction(self.__mainWindowActionManager.actionLog)
        self.__infiniteProgress.setContextMenuPolicy(Qt.ActionsContextMenu)

    def __createProgressDialog(self):
        self.__progress = QProgressDialog(self.__mainWindow)
        self.__progress.setMinimumDuration(500)
        self.__progress.setWindowModality(Qt.WindowModal)
        self.__progress.addAction(self.__mainWindowActionManager.actionLog)
        self.__progress.setContextMenuPolicy(Qt.ActionsContextMenu)

    def getMainWindow(self):
        '''
        Returns the main window object (may be None).
        '''
        return self.__mainWindow

    def getInfiniteProgressDialog(self):
        '''
        Get the main QProgressDialog. It is window-modal, has no cancel
        button and is infinite.
        '''
        if self.__infiniteProgress is None:
            self.__createInfiniteProgressDialog()
        return self.__infiniteProgress

    def getProgressDialog(self):
        '''
        Get the
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
        return self.__logManager

    def statusBarErrorCallback(self, error):
        '''
        Display errors in the status bar of the main window.
        '''
        if isinstance(error, OBSLightBaseError):
            self.sendStatusBarMessage(u"OBS Light error: %s" % error.msg, 30000)
        else:
            self.sendStatusBarMessage(u"Caught exception: %s" % str(error), 30000)

    def popupErrorCallback(self, error, traceback=None):
        '''
        Display errors in a popup. Must be called from UI thread, or
        with a Qt signal.
        '''
        exceptionToMessageBox(error, self.__mainWindow, traceback)

    def sendStatusBarMessage(self, message, timeout=0):
        '''
        Display a message in the status bar of the main window.
        Timeout is in milliseconds.
        '''
        self.__messageSignal.emit(message, timeout)

    def main(self):
        return self.application.exec_()


if __name__ == '__main__':
    gui = Gui()
    gui.main()
