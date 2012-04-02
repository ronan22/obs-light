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
        self.ui_WizardPage.aliasLineEdit.setEnabled(not self.serverAlreadyExists)

    @popupOnException
    def validatePage(self):
        alias = self.field(u"serverAlias")
        srvList = self.manager.getObsServerList()
        if (isNonEmptyString(alias) and (self.serverAlreadyExists or alias not in srvList)):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"green")
            if self.serverAlreadyExists:
                self.callWithInfiniteProgress(self._doModifyServer, "Modifying server")
            else:
                self.callWithInfiniteProgress(self._doAddServer, "Adding server")
            return True
        else:
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
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

    def _doAddServer(self):
        self.manager.addObsServer(self.field(u"apiUrl"),
                                  self.field(u"username"),
                                  self.field(u"password"),
                                  serverRepo=self.field(u"repoUrl"),
                                  alias=self.field(u"serverAlias"),
                                  serverWeb=self.field(u"webUrl"))
    def _doModifyServer(self):
        for fieldName in self.fieldTranslation.keys():
            self.manager.setObsServerParameter(self.field(u"serverAlias"),
                                               self.fieldTranslation[fieldName],
                                               self.field(fieldName))
