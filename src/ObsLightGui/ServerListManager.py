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
Created on 27 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject
from PySide.QtGui import QListWidget, QMessageBox, QPushButton

from ServerConfigManager import ServerConfigManager
from Utils import popupOnException

class ServerListManager(QObject):
    """
    Manage the OBS server list window.
    """
    __gui = None
    __obsLightManager = None
    __srvListDialog = None
    __listWidget = None
    __serverConfigManager = None

    def __init__(self, gui):
        """
        Load and display the OBS server list window.
        """
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = self.__gui.getObsLightManager()
        self.__srvListDialog = self.__gui.loadWindow("obsServerList.ui")
        self.__listWidget = self.__srvListDialog.findChild(QListWidget,
                                                           "obsServersListWidget")
        self.loadServerList()
        addExistingServerButton = self.__srvListDialog.findChild(QPushButton,
                                                                 "addExistingServerButton")
        addExistingServerButton.clicked.connect(self.on_addExistingServerButton_clicked)
        createVirtualServerButton = self.__srvListDialog.findChild(QPushButton,
                                                                   "createVirtualServerButton")
        createVirtualServerButton.clicked.connect(self.on_createVirtualServerButton_clicked)
        modifyServerButton = self.__srvListDialog.findChild(QPushButton,
                                                            "modifyServerButton")
        modifyServerButton.clicked.connect(self.on_modifyServerButton_clicked)
        deleteServerButton = self.__srvListDialog.findChild(QPushButton, "deleteServerButton")
        deleteServerButton.clicked.connect(self.on_deleteServerButton_clicked)
        testServerButton = self.__srvListDialog.findChild(QPushButton, "checkConnectionButton")
        testServerButton.clicked.connect(self.on_testServerButton_clicked)
        self.__srvListDialog.show()

    def loadServerList(self):
        """
        Clear and reload the list of OBS servers into the list widget.
        """
        self.__listWidget.clear()
        self.__listWidget.addItems(self.__obsLightManager.getObsServerList())

    def on_addExistingServerButton_clicked(self):
        self.__serverConfigManager = ServerConfigManager(self.__gui)
        self.__serverConfigManager.finished.connect(self.on_serverConfigManager_finished)

    def on_createVirtualServerButton_clicked(self):
        self.__serverConfigManager = ServerConfigManager(self.__gui)
        self.__serverConfigManager.finished.connect(self.on_serverConfigManager_finished)

    def on_modifyServerButton_clicked(self):
        currentItem = self.__listWidget.currentItem()
        if currentItem is not None:
            self.__serverConfigManager = ServerConfigManager(self.__gui,
                                                             currentItem.text())

    @popupOnException
    def on_deleteServerButton_clicked(self):
        currentItem = self.__listWidget.currentItem()
        if currentItem is not None:
            serverAlias = currentItem.text()
            if len(serverAlias) > 0:
                self.__obsLightManager.delObsServer(serverAlias)
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
                isJoinable = self.__obsLightManager.testServer(serverAlias)
                if isJoinable:
                    QMessageBox.information(None, "Server OK", "Server is reachable")
                else:
                    QMessageBox.warning(None, "Server not reachable", "Server is not reachable")
