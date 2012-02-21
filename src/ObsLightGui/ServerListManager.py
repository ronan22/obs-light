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
Created on 27 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject
from PySide.QtGui import QMessageBox

from ServerConfigManager import ServerConfigManager
from Utils import popupOnException
from ObsLightGuiObject import ObsLightGuiObject

class ServerListManager(QObject, ObsLightGuiObject):
    """
    Manage the OBS server list window.
    """

    def __init__(self, gui):
        """
        Load and display the OBS server list window.
        """
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.__srvListDialog = self.gui.loadWindow(u"obsServerList.ui")
        self.__listWidget = self.__srvListDialog.obsServersListWidget
        self.__serverConfigManager = None
        self.loadServerList()
        sld = self.__srvListDialog
        sld.addExistingServerButton.clicked.connect(self.on_addExistingServerButton_clicked)
        sld.createVirtualServerButton.clicked.connect(self.on_createVirtualServerButton_clicked)
        sld.modifyServerButton.clicked.connect(self.on_modifyServerButton_clicked)
        sld.deleteServerButton.clicked.connect(self.on_deleteServerButton_clicked)
        sld.checkConnectionButton.clicked.connect(self.on_testServerButton_clicked)
        sld.show()

    def loadServerList(self):
        '''
        Clear and reload the list of OBS servers into the list widget.
        '''
        self.__listWidget.clear()
        self.__listWidget.addItems(self.manager.getObsServerList())

    def on_addExistingServerButton_clicked(self):
        self.__serverConfigManager = ServerConfigManager(self.gui)
        self.__serverConfigManager.finished.connect(self.on_serverConfigManager_finished)

    def on_createVirtualServerButton_clicked(self):
        self.__serverConfigManager = ServerConfigManager(self.gui)
        self.__serverConfigManager.finished.connect(self.on_serverConfigManager_finished)

    def on_modifyServerButton_clicked(self):
        currentItem = self.__listWidget.currentItem()
        if currentItem is not None:
            self.__serverConfigManager = ServerConfigManager(self.gui,
                                                             currentItem.text())

    @popupOnException
    def on_deleteServerButton_clicked(self):
        currentItem = self.__listWidget.currentItem()
        if currentItem is not None:
            serverAlias = currentItem.text()
            result = QMessageBox.question(self.mainWindow,
                                      "Are you sure ?",
                                      "Are you sure you want to delete '%s' server ?"
                                        % serverAlias,
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
            if result == QMessageBox.No:
                return
            if len(serverAlias) > 0:
                self.manager.delObsServer(serverAlias)
            self.loadServerList()

    @popupOnException
    def on_serverConfigManager_finished(self, serverListModified):
        if serverListModified:
            self.loadServerList()

    @popupOnException
    def on_testServerButton_clicked(self):
        currentItem = self.__listWidget.currentItem()
        if currentItem is not None:
            serverAlias = currentItem.text()
            if len(serverAlias) > 0:
                isJoinable = self.manager.testServer(serverAlias)
                if isJoinable:
                    QMessageBox.information(None, u"Server OK", u"Server is reachable")
                else:
                    QMessageBox.warning(None, u"Server not reachable", u"Server is not reachable")
