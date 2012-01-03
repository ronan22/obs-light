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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 27 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtGui import QAction, QLabel

from ServerListManager import ServerListManager
from ObsLightGuiObject import ObsLightGuiObject

class MainWindowActionManager(ObsLightGuiObject):
    '''
    Manage the action menu of the main window.
    Connects the actions signals to the appropriate slots.
    '''
    __serverListManager = None
    __aboutDialog = None
    __wizard = None

    actionAbout = None
    actionLog = None
    actionOBS_servers = None
    actionWizard = None

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        mainWindow = self.gui.getMainWindow()
        self.actionOBS_servers = mainWindow.findChild(QAction, u"actionOBS_servers")
        self.actionOBS_servers.triggered.connect(self.on_actionOBS_servers_triggered)
        self.__aboutDialog = self.gui.loadWindow(u"obsLightAbout.ui")
        versionLabel = self.__aboutDialog.findChild(QLabel, "versionLabel")
        versionLabel.setText(u"Version: %s" % self.manager.getVersion())
        self.actionAbout = mainWindow.findChild(QAction, u"actionAbout")
        self.actionAbout.triggered.connect(self.__aboutDialog.show)
        self.actionLog = mainWindow.findChild(QAction, u"actionShow_log")
        self.actionLog.triggered.connect(self.on_actionLog_triggered)
        self.actionWizard = mainWindow.findChild(QAction, u"actionWizard")
        self.actionWizard.triggered.connect(self.on_actionWizard_triggered)

    def on_actionOBS_servers_triggered(self):
        self.__serverListManager = ServerListManager(self.gui)

    def on_actionAbout_triggered(self):
        self.__aboutDialog.show()

    def on_actionLog_triggered(self):
        self.gui.getLogManager().show()

    def on_actionWizard_triggered(self):
        self.gui.runWizard()
