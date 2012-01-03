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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QRegExp, Signal
from PySide.QtGui import QDialog, QDialogButtonBox
from PySide.QtGui import QLineEdit, QPushButton, QRegExpValidator

from ObsLight.ObsLightTools import isNonEmptyString

from Utils import popupOnException, colorizeWidget
from ObsLightGuiObject import ObsLightGuiObject

class ServerConfigManager(QObject, ObsLightGuiObject):
    '''
    Manage an OBS server configuration window.
    '''
    __serverAlias = None
    __srvConfDialog = None
    __checkConnectionButton = None

    __dialogButtonBox = None
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
        ObsLightGuiObject.__init__(self, gui)
        self.__serverAlias = serverAlias
        self.__srvConfDialog = self.gui.loadWindow(u"obsServerConfig.ui")
        self.__loadWidgets()
        if self.__serverAlias is not None:
            self.__loadInitialFieldValues()
        self.__srvConfDialog.finished.connect(self.on_obsServerConfigDialog_finished)
        self.__srvConfDialog.show()

    def __loadWidgets(self):
        self.__dialogButtonBox = self.__srvConfDialog.findChild(QDialogButtonBox,
                                                                "obsServerConfigButtonBox")
        self.disableOkButton()
        self.__webUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               u"serverWebUrlLineEdit")
        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp(u"http[s]?://.+"))
        self.__webUrlLineEdit.setValidator(httpValidator)
        self.__webUrlLineEdit.setPlaceholderText(u"http://myObs")
        self.__webUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__apiUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               u"serverApiLineEdit")
        self.__apiUrlLineEdit.setValidator(httpValidator)
        self.__apiUrlLineEdit.setPlaceholderText(u"http://myObs:81")
        self.__apiUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__repoUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                                u"serverRepoLineEdit")
        self.__repoUrlLineEdit.setValidator(httpValidator)
        self.__repoUrlLineEdit.setPlaceholderText(u"http://myObs:82")
        self.__repoUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__aliasLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                              u"serverAliasLineEdit")
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"\\S+"))
        self.__aliasLineEdit.setValidator(noSpaceValidator)
        self.__userLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                             u"usernameLineEdit")
        self.__passLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                             u"passwordLineEdit")
        self.__checkConnectionButton = self.__srvConfDialog.findChild(QPushButton,
                                                                      u"checkConnectionButton")
        self.__checkConnectionButton.clicked.connect(self.on_checkConnectionButton_clicked)

    def __loadInitialFieldValues(self):
        manager = self.manager
        self.__aliasLineEdit.setText(self.__serverAlias)
        self.__aliasLineEdit.setReadOnly(True)
        self.__webUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                    u"serverWeb"))
        self.__apiUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                    u"serverAPI"))
        self.__repoUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                     u"serverRepo"))
        self.__userLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                  u"user"))
        self.__passLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                  u"passw"))

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
        manager = self.manager
        # User canceled, nothing to do.
        if result == QDialog.Rejected:
            self.finished.emit(False)
        # User accepted, and there was no preloaded server,
        # so create a new server.
        elif self.__serverAlias is None:
            manager.addObsServer(self.getApiUrl(),
                                 self.getUser(),
                                 self.getPass(),
                                 serverRepo=self.getRepoUrl(),
                                 alias=self.getAlias(),
                                 serverWeb=self.getWebIfaceUrl())
            self.finished.emit(True)
        # User accepted, and there was a preloaded server,
        # so modify it.
        else:
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverWeb",
                                          self.getWebIfaceUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverAPI",
                                          self.getApiUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverRepo",
                                          self.getRepoUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"user",
                                          self.getUser())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"passw",
                                          self.getPass())
            self.finished.emit(True)

    def disableOkButton(self, _=None):
        # We need a parameter ^ in order to call this method from textEdited signal
        self.__dialogButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    @popupOnException
    def on_checkConnectionButton_clicked(self):
        def testAndColorizeUrl(url, widget):
            color = u"red"
            isOk = False
            try:
                if not isNonEmptyString(url):
                    color = u"red"
                elif self.manager.testUrl(url):
                    isOk = True
                    color = u"green"
                elif self.manager.testHost(url):
                    color = u"orange"
                else:
                    color = u"red"
            finally:
                colorizeWidget(widget, color)
            return isOk

        def testAndColorizeString(theString, widget):
            isOk = isNonEmptyString(theString)
            colorizeWidget(widget, "green" if isOk else "red")
            return isOk

        web = self.getWebIfaceUrl()
        api = self.getApiUrl()
        repo = self.getRepoUrl()
        user = self.getUser()
        password = self.getPass()
        alias = self.getAlias()

        userPassOk = testAndColorizeString(user, self.__userLineEdit)
        userPassOk = testAndColorizeString(password, self.__passLineEdit) and userPassOk

        allOk = userPassOk
        allOk = testAndColorizeUrl(web, self.__webUrlLineEdit) and allOk
        allOk = testAndColorizeUrl(repo, self.__repoUrlLineEdit) and allOk

        if userPassOk:
            apiRes = self.manager.testApi(api, user, password)
            if apiRes == 1:
                colorizeWidget(self.__userLineEdit, "red")
                colorizeWidget(self.__passLineEdit, "red")
                allOk = False
            elif apiRes == 2:
                colorizeWidget(self.__apiUrlLineEdit, "red")
                colorizeWidget(self.__userLineEdit, "orange")
                colorizeWidget(self.__passLineEdit, "orange")
                allOk = False
            else:
                colorizeWidget(self.__apiUrlLineEdit, "green")
                colorizeWidget(self.__userLineEdit, "green")
                colorizeWidget(self.__passLineEdit, "green")

        srvList = self.manager.getObsServerList()
        if (isNonEmptyString(alias) and
                (alias == self.__serverAlias or self.getAlias() not in srvList)):
            colorizeWidget(self.__aliasLineEdit, "green")
        else:
            allOk = False
            colorizeWidget(self.__aliasLineEdit, "red")

        self.__dialogButtonBox.button(QDialogButtonBox.Ok).setEnabled(allOk)
