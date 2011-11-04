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

from Utils import popupOnException

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

    @popupOnException
    def on_deleteServerButton_clicked(self):
        # TODO: implement server deletion
        pass

    @popupOnException
    def on_serverConfigManager_finished(self, serverListModified):
        if serverListModified:
            self.loadServerList()


class ServerConfigManager(QObject):
    '''
    Manage an OBS server configuration window.
    '''
    __gui = None
    __serverAlias = None
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
        Load the server configuration window.
        If serverAlias is None, load an empty configuration.
        If serverAlias is an OBS server alias, load its configuration.
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__serverAlias = serverAlias
        self.__srvConfDialog = self.__gui.loadWindow("obsServerConfig.ui")
        self.__loadFieldObjects()
        if self.__serverAlias is not None:
            self.__loadInitialFieldValues()
        self.__srvConfDialog.finished.connect(self.on_obsServerConfigDialog_finished)
        self.__srvConfDialog.show()
        
    def __loadFieldObjects(self):
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
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp("\\S+"))
        self.__aliasLineEdit.setValidator(noSpaceValidator)
        self.__userLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "usernameLineEdit")
        self.__passLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               "passwordLineEdit")
        
    def __loadInitialFieldValues(self):
        manager = self.__gui.getObsLightManager()
        self.__aliasLineEdit.setText(self.__serverAlias)
        self.__aliasLineEdit.setReadOnly(True)
        self.__webUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias, "serverWeb"))
        self.__apiUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias, "serverAPI"))
        self.__repoUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias, "serverRepo"))
        self.__userLineEdit.setText(manager.getObsServerParameter(self.__serverAlias, "user"))
        self.__passLineEdit.setText(manager.getObsServerParameter(self.__serverAlias, "passw"))

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

    @popupOnException
    def on_obsServerConfigDialog_finished(self, result):
        # User canceled, nothing to do.
        if result == QDialog.Rejected:
            self.finished.emit(False)
        # User accepted, and there was no preloaded server,
        # so create a new server.
        elif self.__serverAlias is None:
            manager = self.__gui.getObsLightManager()
            manager.addObsServer(self.getApiUrl(), self.getUser(), self.getPass(),
                                 serverRepo=self.getRepoUrl(),
                                 alias=self.getAlias(),
                                 serverWeb=self.getWebIfaceUrl())
            self.finished.emit(True)
        # User accepted, and there was a preloaded server,
        # so modify it.
        else:
            manager = self.__gui.getObsLightManager()
            manager.setObsServerParameter(self.__serverAlias, "serverWeb", self.getWebIfaceUrl())
            manager.setObsServerParameter(self.__serverAlias, "serverAPI", self.getApiUrl())
            manager.setObsServerParameter(self.__serverAlias, "serverRepo", self.getRepoUrl())
            manager.setObsServerParameter(self.__serverAlias, "user", self.getUser())
            manager.setObsServerParameter(self.__serverAlias, "passw", self.getPass())
            self.finished.emit(True)
