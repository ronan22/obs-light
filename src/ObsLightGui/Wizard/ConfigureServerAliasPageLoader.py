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

from PySide.QtGui import QLabel, QLineEdit

from ObsLightGui.Utils import colorizeWidget, isNonEmptyString, uiFriendly, popupOnException

from WizardPageLoader import WizardPageLoader

class ConfigureServerAliasPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_configServerAlias.ui")
        self.aliasLineEdit = self.page.findChild(QLineEdit, u"aliasLineEdit")
        self.webUrlLabel = self.page.findChild(QLabel, u"webUrlLabel")
        self.apiUrlLabel = self.page.findChild(QLabel, u"apiUrlLabel")
        self.repoUrlLabel = self.page.findChild(QLabel, u"repoUrlLabel")
        self.usernameLabel = self.page.findChild(QLabel, u"usernameLabel")
        self.page.registerField(u"serverAlias*", self.aliasLineEdit)
        self.page.initializePage = self._initializePage
        self.page.validatePage = self._validatePage
        self.page.setCommitPage(True)

    def _initializePage(self):
        linkString = u'<a href="%s">%s</a>'
        webUrl = self.page.field(u"webUrl")
        self.webUrlLabel.setText(linkString % (webUrl, webUrl))
        apiUrl = self.page.field(u"apiUrl")
        self.apiUrlLabel.setText(linkString % (apiUrl, apiUrl))
        repoUrl = self.page.field(u"repoUrl")
        self.repoUrlLabel.setText(linkString % (repoUrl, repoUrl))
        username = self.page.field(u"username")
        self.usernameLabel.setText(username)

    @popupOnException
    def _validatePage(self):
        alias = self.page.field(u"serverAlias")
        srvList = self.manager.getObsServerList()
        if (isNonEmptyString(alias) and alias not in srvList):
            colorizeWidget(self.aliasLineEdit, u"green")
            self._addServer()
            return True
        else:
            colorizeWidget(self.aliasLineEdit, u"red")
            return False


    def _addServer(self):
        self.waitWhile(self._doAddServer)

    @uiFriendly()
    def _doAddServer(self):
        self.manager.addObsServer(self.page.field(u"apiUrl"),
                                  self.page.field(u"username"),
                                  self.page.field(u"password"),
                                  serverRepo=self.page.field(u"repoUrl"),
                                  alias=self.page.field(u"serverAlias"),
                                  serverWeb=self.page.field(u"webUrl"))
