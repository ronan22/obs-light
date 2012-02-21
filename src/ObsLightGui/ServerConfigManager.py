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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Signal
from PySide.QtGui import QDialog, QDialogButtonBox, QRegExpValidator

from ObsLight.ObsLightUtils import isNonEmptyString

from Utils import popupOnException, colorizeWidget, SERVER_ALIAS_REGEXP, URL_REGEXP
from ObsLightGuiObject import ObsLightGuiObject

class ServerConfigManager(QObject, ObsLightGuiObject):
    '''
    Manage an OBS server configuration window.
    '''

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
        self.disableOkButton()
        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(URL_REGEXP)
        self.__srvConfDialog.serverWebUrlLineEdit.setValidator(httpValidator)
        self.__srvConfDialog.serverWebUrlLineEdit.setPlaceholderText(u"http://myObs")
        self.__srvConfDialog.serverWebUrlLineEdit.textEdited.connect(self.disableOkButton)

        self.__srvConfDialog.serverApiLineEdit.setValidator(httpValidator)
        self.__srvConfDialog.serverApiLineEdit.setPlaceholderText(u"http://myObs:81")
        self.__srvConfDialog.serverApiLineEdit.textEdited.connect(self.disableOkButton)

        self.__srvConfDialog.serverRepoLineEdit.setValidator(httpValidator)
        self.__srvConfDialog.serverRepoLineEdit.setPlaceholderText(u"http://myObs:82")
        self.__srvConfDialog.serverRepoLineEdit.textEdited.connect(self.disableOkButton)

        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(SERVER_ALIAS_REGEXP)
        self.__srvConfDialog.serverAliasLineEdit.setValidator(noSpaceValidator)

        self.__srvConfDialog.checkConnectionButton.clicked.connect(self.on_checkConnectionButton_clicked)

    def __loadInitialFieldValues(self):
        manager = self.manager
        scd = self.__srvConfDialog
        scd.serverAliasLineEdit.setText(self.__serverAlias)
        scd.serverAliasLineEdit.setReadOnly(True)
        scd.serverWebUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                       "serverWeb"))
        scd.serverApiLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                    "serverAPI"))
        scd.serverRepoLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                     "serverRepo"))
        scd.usernameLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                   "user"))
        scd.passwordLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                   "passw"))

    def getWebIfaceUrl(self):
        return self.__srvConfDialog.serverWebUrlLineEdit.text()

    def getApiUrl(self):
        return self.__srvConfDialog.serverApiLineEdit.text()

    def getRepoUrl(self):
        return self.__srvConfDialog.serverRepoLineEdit.text()

    def getAlias(self):
        return self.__srvConfDialog.serverAliasLineEdit.text()

    def getUser(self):
        return self.__srvConfDialog.usernameLineEdit.text()

    def getPass(self):
        return self.__srvConfDialog.passwordLineEdit.text()

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
                                          "serverWeb",
                                          self.getWebIfaceUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          "serverAPI",
                                          self.getApiUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          "serverRepo",
                                          self.getRepoUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          "user",
                                          self.getUser())
            manager.setObsServerParameter(self.__serverAlias,
                                          "passw",
                                          self.getPass())
            self.finished.emit(True)

    def disableOkButton(self, _=None):
        # We need a parameter ^ in order to call this method from textEdited signal
        self.__srvConfDialog.obsServerConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

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

        scd = self.__srvConfDialog

        userPassOk = testAndColorizeString(user, scd.usernameLineEdit)
        userPassOk = testAndColorizeString(password, scd.passwordLineEdit) and userPassOk

        allOk = userPassOk
        allOk = testAndColorizeUrl(web, scd.serverWebUrlLineEdit) and allOk
        allOk = testAndColorizeUrl(repo, scd.serverRepoLineEdit) and allOk

        if userPassOk:
            apiRes = self.manager.testApi(api, user, password)
            if apiRes == 1:
                colorizeWidget(scd.usernameLineEdit, "red")
                colorizeWidget(scd.passwordLineEdit, "red")
                allOk = False
            elif apiRes == 2:
                colorizeWidget(scd.serverApiLineEdit, "red")
                colorizeWidget(scd.usernameLineEdit, "orange")
                colorizeWidget(scd.passwordLineEdit, "orange")
                allOk = False
            else:
                colorizeWidget(scd.serverApiLineEdit, "green")
                colorizeWidget(scd.usernameLineEdit, "green")
                colorizeWidget(scd.passwordLineEdit, "green")

        srvList = self.manager.getObsServerList()
        if (isNonEmptyString(alias) and
                (alias == self.__serverAlias or self.getAlias() not in srvList)):
            colorizeWidget(scd.serverAliasLineEdit, "green")
        else:
            allOk = False
            colorizeWidget(scd.serverAliasLineEdit, "red")

        scd.obsServerConfigButtonBox.button(QDialogButtonBox.Ok).setEnabled(allOk)
