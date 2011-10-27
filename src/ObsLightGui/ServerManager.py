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

from PySide.QtCore import QObject, QRegExp, Signal
from PySide.QtGui import QDialog, QLineEdit, QListWidget, QPushButton
from PySide.QtGui import QRegExpValidator

class ServerListManager(QObject):
    '''
    Manage the OBS server list window.
    '''
    __gui = None
    __obsLightManager = None
    __srvListDialog = None
    __listWidget = None
    __serverConfigManager = None

    def __init__(self, gui):
        '''
        Load and display the OBS server list window.
        '''
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
        self.__srvListDialog.show()

    def loadServerList(self):
        '''
        Clear and reload the list of OBS servers into the list widget.
        '''
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

    def on_deleteServerButton_clicked(self):
        pass
    
    def on_serverConfigManager_finished(self, serverListModified):
        if serverListModified:
            self.loadServerList()


class ServerConfigManager(QObject):
    '''
    Manage an OBS server configuration window.
    '''
    __gui = None
    __srvConfDialog = None

    __webUrlLineEdit = None
    __apiUrlLineEdit = None
    __repoUrlLineEdit = None
    __aliasLineEdit = None
    __userLineEdit = None
    __passLineEdit = None
    
    finished = Signal(bool)

    def __init__(self, gui, serverAlias=None):
        '''
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__srvConfDialog = self.__gui.loadWindow("obsServerConfig.ui")
        self.__webUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "serverWebUrlLineEdit")
        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp("http[s]?://.+"))
        self.__webUrlLineEdit.setValidator(httpValidator)
        self.__webUrlLineEdit.setPlaceholderText("http://myObs")
        self.__apiUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "serverApiLineEdit")
        self.__apiUrlLineEdit.setValidator(httpValidator)
        self.__apiUrlLineEdit.setPlaceholderText("http://myObs:81")
        self.__repoUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "serverRepoLineEdit")
        self.__repoUrlLineEdit.setValidator(httpValidator)
        self.__repoUrlLineEdit.setPlaceholderText("http://myObs:82")
        self.__aliasLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "serverAliasLineEdit")
        if serverAlias is not None:
            self.__loadFields(serverAlias)
        self.__userLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "usernameLineEdit")
        self.__passLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "passwordLineEdit")

        self.__srvConfDialog.finished.connect(self.on_obsServerConfigDialog_finished)
        self.__srvConfDialog.show()
        
    def __loadFields(self, serverAlias):
        self.__aliasLineEdit.setText(serverAlias)

    def getWebIfaceUrl(self):
        return self.__webUrlLineEdit.text()
    
    def getApiUrl(self):
        return self.__apiUrlLineEdit.text()
    
    def getRepoUrl(self):
        return self.__repoUrlLineEdit.text()
    
    def getAlias(self):
        return self.__aliasLineEdit.text()
    
    def getUser(self):
        return self.__userLineEdit.text()
    
    def getPass(self):
        return self.__passLineEdit.text()

    def on_obsServerConfigDialog_finished(self, result):
        if result == QDialog.Rejected:
            self.finished.emit(False)
        else:
            manager = self.__gui.getObsLightManager()
            manager.addObsServer(serverWeb=self.getWebIfaceUrl(),
                                 serverAPI=self.getApiUrl(),
                                 serverRepos=self.getRepoUrl(),
                                 aliases=self.getAlias(),
                                 user=self.getUser(),
                                 passw=self.getPass())
            self.finished.emit(True)
