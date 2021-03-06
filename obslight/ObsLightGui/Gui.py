# -*- coding: utf8 -*-
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
Created on 27 sept. 2011

@author: Florent Vennetier
'''

from os.path import dirname, join

from PySide.QtCore import QIODevice, QFile, QMetaObject, QObject, QSettings, Qt, Signal
from PySide.QtGui import QColor, QPixmap, QSplashScreen, QStatusBar
from PySide.QtUiTools import QUiLoader

from ObsLight.ObsLightErr import OBSLightBaseError

from ObsLightGuiMainWindow import ObsLightGuiMainWindow
from ObsLightGuiProgressDialog import ObsLightGuiProgressDialog
from ObsProjectsManager import ObsProjectsManager
from MicProjectsManager import MicProjectsManager
from ActionManager import MainWindowActionManager
from LogManager import LogManager
from Utils import exceptionToMessageBox
from Wizard.ConfigWizard import ConfigWizard

UI_PATH = join(dirname(__file__), u"ui")


class Gui(QObject):
    '''
    ObsLight GUI main class. Keeps reference to the main window
    and to the ObsLightManager.
    '''

    # signal to display a message in the status bar of the main window
    __messageSignal = Signal((str, int))

    def __init__(self, qApplication):
        QObject.__init__(self)
        self.application = qApplication
        self.application.aboutToQuit.connect(self.__beforeQuitting)
        self.uiLoader = QUiLoader()
        # Need to set working directory in order to load icons
        self.uiLoader.setWorkingDirectory(UI_PATH)
        self.uiLoader.registerCustomWidget(ObsLightGuiMainWindow)
        self.uiLoader.registerCustomWidget(ObsLightGuiProgressDialog)

        # loaded in loadManager()
        self.splash = None
        self.__obsLightManager = None
        self.__obsProjectManager = None
        self.__micProjectsManager = None
        self.__logManager = None

        # loaded in __loadMainWindow()
        self.__mainWindow = None
        self.__mainWindowActionManager = None
        self.__statusBar = None

        # loaded in __createInfiniteProgressDialog()
        self.__infiniteProgress = None
        # loaded in __createProgressDialog()
        self.__progress = None

        # loaded in runWizard()
        self.__wizard = None

    def __beforeQuitting(self):
        """
        Method called before the main QApplication quits.
        It disconnects the LogManager.
        """
        self.__logManager.disconnectLogger()

    def loadWindow(self, uiFile, mainWindowAsParent=True, connectSlots=True):
        '''
        Load a Window from UI file.
        '''
        path = join(UI_PATH, uiFile)
        windowFile = QFile(path)
        windowFile.open(QIODevice.ReadOnly | QIODevice.Text)
        # Make all loaded windows children of mainWindow, except mainWindow itself
        window = self.uiLoader.load(windowFile, self.__mainWindow if mainWindowAsParent else None)
        windowFile.close()
        if connectSlots:
            QMetaObject.connectSlotsByName(window)
        return window

    def __loadMainWindow(self):
        self.__mainWindow = self.loadWindow(u"obsLightMain.ui")
        self.__mainWindowActionManager = MainWindowActionManager(self)
        self.__statusBar = self.__mainWindow.findChild(QStatusBar, u"mainStatusBar")
        self.__messageSignal.connect(self.__statusBar.showMessage)
        self.__loadGeometry()
        self.__mainWindow.show()



    def __loadGeometry(self):
        settings = QSettings("Intel_OTC", "obslightgui")
        propMap = {"mainWindow/geometry": self.__mainWindow.restoreGeometry,
                   "mainWindow/state": self.__mainWindow.restoreState,
                   "mainWindow/splitter2State": self.__mainWindow.splitter_2.restoreState,
                   "mainWindow/splitter3State": self.__mainWindow.splitter_3.restoreState,
                   "mainWindow/splitter4State": self.__mainWindow.splitter_4.restoreState,
                   "mainWindow/splitter5State": self.__mainWindow.splitter_5.restoreState,
                   "mainWindow/splitter6State": self.__mainWindow.splitter_6.restoreState,
                   "mainWindow/splitterState": self.__mainWindow.splitter.restoreState,
                   "mainWindow/splitterGeo": self.__mainWindow.splitter.restoreGeometry,
                   "logWindow/geometry": self.__logManager.restoreGeometry}

        for propName, func in propMap.iteritems():
            prop = settings.value(propName)
            if prop is not None:
                func(prop)

    def __saveGeometry(self):
        settings = QSettings("Intel_OTC", "obslightgui")
        propMap = {"mainWindow/geometry": self.__mainWindow.saveGeometry,
                   "mainWindow/state": self.__mainWindow.saveState,
                   "mainWindow/splitter2State": self.__mainWindow.splitter_2.saveState,
                   "mainWindow/splitter3State": self.__mainWindow.splitter_3.saveState,
                   "mainWindow/splitter4State": self.__mainWindow.splitter_4.saveState,
                   "mainWindow/splitter5State": self.__mainWindow.splitter_5.saveState,
                   "mainWindow/splitter6State": self.__mainWindow.splitter_6.saveState,
                   "mainWindow/splitterState": self.__mainWindow.splitter.saveState,
                   "mainWindow/splitterGeo": self.__mainWindow.splitter.saveGeometry,
                   "logWindow/geometry": self.__logManager.saveGeometry}

        for propName, func in propMap.iteritems():
            settings.setValue(propName, func())

    def __createInfiniteProgressDialog(self):
        self.__infiniteProgress = self.loadWindow("obsLightProgress.ui", True)
        self.__infiniteProgress.connectButtons()
        self.__infiniteProgress.setMinimumDuration(500)
        self.__infiniteProgress.setWindowModality(Qt.WindowModal)
        self.__infiniteProgress.showCancelButton(False)
        # make the progress "infinite"
        self.__infiniteProgress.setRange(0, 0)
        showLogSlot = self.__mainWindowActionManager.actionLog.trigger
        self.__infiniteProgress.showLogButton.clicked.connect(showLogSlot)

    def __createProgressDialog(self):
        self.__progress = self.loadWindow("obsLightProgress.ui", True)
        self.__progress.connectButtons()
        self.__progress.setMinimumDuration(500)
        self.__progress.setWindowModality(Qt.WindowModal)
        # make the progress "finite"
        self.__progress.setRange(0, 1)
        showLogSlot = self.__mainWindowActionManager.actionLog.trigger
        self.__progress.showLogButton.clicked.connect(showLogSlot)

    @property
    def mainWindow(self):
        '''
        Returns the main window object (may be None).
        '''
        return self.__mainWindow

    def getInfiniteProgressDialog(self):
        '''
        Get a reference to the main QProgressDialog.
        It is window-modal, has no cancel button and is infinite.
        '''
        if self.__infiniteProgress is None:
            self.__createInfiniteProgressDialog()
        return self.__infiniteProgress

    def getProgressDialog(self):
        '''
        Get a reference to a QProgressDialog instance.
        This progress dialog is window-modal and has a cancel button.
        '''
        if self.__progress is None:
            self.__createProgressDialog()
        return self.__progress

    @property
    def manager(self):
        """
        Get a reference to the unique ObsLightManager instance.
        """
        return self.__obsLightManager

    def getLogManager(self):
        """
        Get a reference to the LogManager instance.
        """
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

    def showLogWindow(self):
        """
        Show the log window. If it is already opened, try to get it
        at foreground.
        """
        self.__mainWindowActionManager.actionLog.trigger()

    def processEvents(self):
        """
        Call QApplication.processEvents().
        To be used if a function prevents the UI thread from
        returning to its event loop.
        """
        self.application.processEvents()

    def refresh(self):
        self.__obsProjectManager.refresh()

    def setCurrentProject(self, projectName):
        self.__obsProjectManager.currentProject = projectName

    def runWizard(self):
        """
        Run the OBS project creation wizard.
        If `autoSelectProject` is the name of an existing OBS Light
        project, go directly to the package selection page of the wizard.
        Returns the QWizard instance.
        """
        self.__wizard = ConfigWizard(self)
        self.__wizard.accepted.connect(self.refresh)
        self.__wizard.show()
        return self.__wizard

    def runWizardToAddPackage(self, project, newPackage=False):
        self.__wizard = ConfigWizard(self)
        self.__wizard.accepted.connect(self.refresh)
        if newPackage:
            self.__wizard.skipToPackageCreation(project)
        else:
            self.__wizard.skipToPackageSelection(project)

        self.__wizard.show()
        return self.__wizard

    def runWizardToConfigureServer(self, parent=None, **prefilledValues):
        """
        Run wizard and skip to server creation page. `parent` is the widget
        to use as parent for the wizard (None -> main window).
        `prefilledValues` allows to specify
        already known server configuration values. Possible keys
        for `prefilledValues`: "webUrl", "apiUrl", "repoUrl", "username",
        "password", "serverAlias".
        Returns the QWizard instance.
        """
        self.__wizard = ConfigWizard(self, parent)
        self.__wizard.skipToServerCreation(**prefilledValues)
        self.__wizard.show()
        return self.__wizard

    def loadManager(self, methodToGetManager, *args, **kwargs):
        """
        Show splash screen while calling `methodToGetManager(*args, **kwargs)`
        to get a reference to the ObsLightManager.
        """
        pixmap = QPixmap(join(UI_PATH, "splashscreen.png"))
        self.splash = QSplashScreen(pixmap)
        self.splash.show()
        self.processEvents()
        self.splash.showMessage(u"Loading...",
                                Qt.AlignBottom | Qt.AlignHCenter,
                                QColor(u"white"))
        self.processEvents()
        self.__obsLightManager = methodToGetManager(*args, **kwargs)
        self.__logManager = LogManager(self)
        self.__loadMainWindow()
        self.__obsProjectManager = ObsProjectsManager(self)
        self.__micProjectsManager = MicProjectsManager(self)
        self.__mainWindow.callBeforeCloseEvent.append(self.__saveGeometry)
        self.__mainWindow.callBeforeCloseEvent.append(self.__logManager.close)
        self.splash.finish(self.mainWindow)

    def main(self):
        return self.application.exec_()


if __name__ == '__main__':
    gui = Gui()
    gui.main()
