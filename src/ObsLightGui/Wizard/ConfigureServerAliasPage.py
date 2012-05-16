# -*- coding: utf8 -*-
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
Created on 20 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, popupOnException, SERVER_ALIAS_REGEXP
from ObsLight.ObsLightUtils import isNonEmptyString

from WizardPageWrapper import ObsLightWizardPage

class ConfigureServerAliasPage(ObsLightWizardPage):

    fieldTranslation = {u"webUrl": "serverWeb",
                        u"apiUrl": "serverAPI",
                        u"repoUrl": "serverRepo",
                        u"username": "user",
                        u"password": "passw"}

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configServerAlias.ui")
        noSpaceValidator = QRegExpValidator(SERVER_ALIAS_REGEXP, self)
        self.ui_WizardPage.aliasLineEdit.setValidator(noSpaceValidator)
        self.registerField(u"serverAlias*", self.ui_WizardPage.aliasLineEdit)
        self.setCommitPage(True)
        self.serverAlreadyExists = False

    def initializePage(self):
        self.serverAlreadyExists = isNonEmptyString(self.field(u"serverAlias"))
        linkString = u'<a href="%s">%s</a>'
        webUrl = self.field(u"webUrl")
        self.ui_WizardPage.webUrlLabel.setText(linkString % (webUrl, webUrl))
        apiUrl = self.field(u"apiUrl")
        self.ui_WizardPage.apiUrlLabel.setText(linkString % (apiUrl, apiUrl))
        repoUrl = self.field(u"repoUrl")
        self.ui_WizardPage.repoUrlLabel.setText(linkString % (repoUrl, repoUrl))
        username = self.field(u"username")
        self.ui_WizardPage.usernameLabel.setText(username)
        # If we are modifying an existing server, do not allow to change alias
        self.ui_WizardPage.aliasLineEdit.setEnabled(not self.serverAlreadyExists)
        # and hide tips about aliases
        self.ui_WizardPage.aliasColorsLabel.setVisible(not self.serverAlreadyExists)
        self.ui_WizardPage.pleaseEnterAliasLabel.setVisible(not self.serverAlreadyExists)

    @popupOnException
    def isComplete(self):
        return super(ConfigureServerAliasPage, self).isComplete() and self.checkAlias()

    @popupOnException
    def validatePage(self):
        if self.checkAlias():
            if self.serverAlreadyExists:
                self.callWithInfiniteProgress(self._doModifyServer, "Modifying server")
            else:
                self.callWithInfiniteProgress(self._doAddServer, "Adding server")
            return True
        else:
            return False

    def nextId(self):
        # We did not start at the beginning, so we probably want
        # to just add or modify a server, not do the whole wizard.
        if self.wizard().startId() > 0:
            return -1
        else:
            return super(ConfigureServerAliasPage, self).nextId()

    def cleanupPage(self):
        pass

    def checkAlias(self):
        """
        Check if alias is non-empty, and in case user is adding a new server,
        that the alias does not already exist. Colorizes widget in green and
        returns True in case of success, colorizes widget in red and returns
        False otherwise.
        """
        alias = self.field(u"serverAlias")
        srvList = self.manager.getObsServerList()
        if isNonEmptyString(alias) and (self.serverAlreadyExists or alias not in srvList):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"green")
            return True
        else:
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

    def _doAddServer(self):
        # Some functions may not appreciate unicode so we cast fields to str
        self.manager.addObsServer(str(self.field(u"apiUrl")),
                                  str(self.field(u"username")),
                                  str(self.field(u"password")),
                                  serverRepo=str(self.field(u"repoUrl")),
                                  alias=str(self.field(u"serverAlias")),
                                  serverWeb=str(self.field(u"webUrl")))
    def _doModifyServer(self):
        for fieldName in self.fieldTranslation.keys():
            self.manager.setObsServerParameter(str(self.field(u"serverAlias")),
                                               self.fieldTranslation[fieldName],
                                               str(self.field(fieldName)))
