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

from PySide.QtCore import QRegExp
from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, uiFriendly, popupOnException
from ObsLight.ObsLightUtils import isNonEmptyString

from WizardPageWrapper import ObsLightWizardPage

class ConfigureServerAliasPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configServerAlias.ui")
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"[^\\s:]+"))
        self.ui_WizardPage.aliasLineEdit.setValidator(noSpaceValidator)
        self.registerField(u"serverAlias*", self.ui_WizardPage.aliasLineEdit)
        self.setCommitPage(True)

    def initializePage(self):
        linkString = u'<a href="%s">%s</a>'
        webUrl = self.field(u"webUrl")
        self.ui_WizardPage.webUrlLabel.setText(linkString % (webUrl, webUrl))
        apiUrl = self.field(u"apiUrl")
        self.ui_WizardPage.apiUrlLabel.setText(linkString % (apiUrl, apiUrl))
        repoUrl = self.field(u"repoUrl")
        self.ui_WizardPage.repoUrlLabel.setText(linkString % (repoUrl, repoUrl))
        username = self.field(u"username")
        self.ui_WizardPage.usernameLabel.setText(username)

    @popupOnException
    def validatePage(self):
        alias = self.field(u"serverAlias")
        srvList = self.manager.getObsServerList()
        if (isNonEmptyString(alias) and alias not in srvList):
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"green")
            self._addServer()
            return True
        else:
            colorizeWidget(self.ui_WizardPage.aliasLineEdit, u"red")
            return False

    def _addServer(self):
        self.setBusyCursor(self._doAddServer)

    @uiFriendly()
    def _doAddServer(self):
        self.manager.addObsServer(self.field(u"apiUrl"),
                                  self.field(u"username"),
                                  self.field(u"password"),
                                  serverRepo=self.field(u"repoUrl"),
                                  alias=self.field(u"serverAlias"),
                                  serverWeb=self.field(u"webUrl"))
