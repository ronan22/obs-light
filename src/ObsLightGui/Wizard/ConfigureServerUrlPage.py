# -*- coding: utf8 -*-
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
Created on 19 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, removeEffect, URL_REGEXP
from ObsLight.ObsLightUtils import isNonEmptyString

from WizardPageWrapper import ObsLightWizardPage

class ConfigureServerUrlPage(ObsLightWizardPage):

    isOk = True
    fieldTranslation = {u"webUrl": "serverWeb",
                        u"apiUrl": "serverAPI",
                        u"repoUrl": "serverRepo",
                        u"username": "user",
                        u"password": "passw"}
    # FIXME: the following list should be moved somewhere else
    # The first element is empty, so it can be used to clean fields
    preConfiguredServerList = [{"serverAlias": "",
                                "webUrl": "",
                                "apiUrl": "",
                                "repoUrl": "",
                                "username": "",
                                "password": ""},
                               {"serverAlias": "meego.com",
                                "webUrl": "https://build.meego.com",
                                "apiUrl": "https://api.meego.com",
                                "repoUrl": "http://download.meego.com/live"},
                               {"serverAlias": "pub.meego.com",
                                "webUrl": "https://build.pub.meego.com",
                                "apiUrl": "https://api.pub.meego.com",
                                "repoUrl": "http://repo.pub.meego.com"},
                               {"serverAlias": "opensuse.org",
                                "webUrl": "https://build.opensuse.org",
                                "apiUrl": "https://api.opensuse.org",
                                "repoUrl": "http://download.opensuse.org/repositories"},
                               {"serverAlias": "obslightserver",
                                "webUrl": "https://obslightserver",
                                "apiUrl": "https://obslightserver:444",
                                "repoUrl": "http://obslightserver:82",
                                "username": "obsuser",
                                "password": "opensuse"}]

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configServerUrl.ui")

        httpValidator = QRegExpValidator(URL_REGEXP, self)
        self.ui_WizardPage.webUrlLineEdit.setValidator(httpValidator)
        self.ui_WizardPage.apiUrlLineEdit.setValidator(httpValidator)
        self.ui_WizardPage.repoUrlLineEdit.setValidator(httpValidator)
        for pc in self.preConfiguredServerList:
            self.ui_WizardPage.preConfiguredServerCBox.addItem(pc['serverAlias'], pc)
        self.ui_WizardPage.preConfiguredServerCBox.currentIndexChanged.connect(self.autoConfServer)

        self.registerField(u"webUrl*", self.ui_WizardPage.webUrlLineEdit)
        self.registerField(u"apiUrl*", self.ui_WizardPage.apiUrlLineEdit)
        self.registerField(u"repoUrl*", self.ui_WizardPage.repoUrlLineEdit)
        self.registerField(u"username*", self.ui_WizardPage.usernameLineEdit)
        self.registerField(u"password*", self.ui_WizardPage.passwordLineEdit)

    def initializePage(self):
        super(ConfigureServerUrlPage, self).initializePage()
        self.loadKnownFields()
        self._clearEffects()

    def loadKnownFields(self):
        serverAlias = self.field(u"serverAlias")
        if isNonEmptyString(serverAlias):
            for fieldName in self.fieldTranslation.keys():
                if not isNonEmptyString(self.field(fieldName)):
                    value = self.manager.getObsServerParameter(serverAlias,
                                                               self.fieldTranslation[fieldName])
                    self.setField(fieldName, value)

    def cleanupPage(self):
        pass

    def validatePage(self):
        self._clearEffects()
        self.setBusyCursor(self.doValidatePage)
        return self.isOk

    def autoConfServer(self, index):
        """Load pre-configured values in wizard fields"""
        configDict = self.preConfiguredServerList[index]
        if self.wizard().isModifyingServer:
            # If we are modifying an existing server, don't change its alias
            configDict.pop('serverAlias', None)
        for fieldName, value in configDict.iteritems():
            self.setField(fieldName, value)

    def _clearEffects(self):
        removeEffect(self.ui_WizardPage.apiUrlLineEdit)
        removeEffect(self.ui_WizardPage.repoUrlLineEdit)
        removeEffect(self.ui_WizardPage.webUrlLineEdit)

    def _friendlyTestUrl(self, url, message="Testing %s"):
        return self.callWithInfiniteProgress(self.manager.testUrl,
                                             message % url,
                                             url)

    def _friendlyTestHost(self, url, message="Testing host of %s"):
        return self.callWithInfiniteProgress(self.manager.testHost,
                                             message % url,
                                             url)

    def _friendlyTestApi(self, url, user, password,
                         message="Testing API %s with user/password"):
        return self.callWithInfiniteProgress(self.manager.testApi,
                                             message % url,
                                             url, user, password)

    def doValidatePage(self):
        def testAndColorizeUrl(url, widget):
            # Green -> OK
            # Orange -> Host OK but wrong URL
            # Red -> Wrong host
            color = u"red"
            isOk = False
            try:
                if not isNonEmptyString(url):
                    color = u"red"
                elif self._friendlyTestUrl(url):
                    isOk = True
                    color = u"green"
                elif self._friendlyTestHost(url):
                    color = u"orange"
                else:
                    color = u"red"
            except BaseException as e:
                print e
            finally:
                colorizeWidget(widget, color)
            return isOk

        def testAndColorizeString(theString, widget):
            isOk = isNonEmptyString(theString)
            colorizeWidget(widget, u"green" if isOk else u"red")
            return isOk

        web = self.field(u"webUrl")
        api = self.field(u"apiUrl")
        repo = self.field(u"repoUrl")
        user = self.field(u"username")
        password = self.field(u"password")

        userPassOk = testAndColorizeString(user, self.ui_WizardPage.usernameLineEdit)
        userPassOk = testAndColorizeString(password, self.ui_WizardPage.passwordLineEdit) and userPassOk

        allOk = userPassOk
        allOk = testAndColorizeUrl(web, self.ui_WizardPage.webUrlLineEdit) and allOk
        allOk = testAndColorizeUrl(repo, self.ui_WizardPage.repoUrlLineEdit) and allOk

        if userPassOk:
            apiRes = self._friendlyTestApi(api, user, password)
            if apiRes == 1:
                colorizeWidget(self.ui_WizardPage.apiUrlLineEdit, u"green")
                colorizeWidget(self.ui_WizardPage.usernameLineEdit, u"red")
                colorizeWidget(self.ui_WizardPage.passwordLineEdit, u"red")
                allOk = False
            elif apiRes == 2:
                colorizeWidget(self.ui_WizardPage.apiUrlLineEdit, u"red")
                colorizeWidget(self.ui_WizardPage.usernameLineEdit, u"orange")
                colorizeWidget(self.ui_WizardPage.passwordLineEdit, u"orange")
                allOk = False
            else:
                colorizeWidget(self.ui_WizardPage.apiUrlLineEdit, u"green")
                colorizeWidget(self.ui_WizardPage.usernameLineEdit, u"green")
                colorizeWidget(self.ui_WizardPage.passwordLineEdit, u"green")

        self.isOk = allOk
        if not allOk:
            self.gui.showLogWindow()
