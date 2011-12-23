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
Created on 19 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QRegExp
from PySide.QtGui import QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, removeEffect, isNonEmptyString, uiFriendly

from WizardPageWrapper import ObsLightWizardPage

class ConfigureServerUrlPage(ObsLightWizardPage):

    isOk = True

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_configServerUrl.ui")

        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp(u"http[s]?://.+"))
        self.ui_WizardPage.webUrlLineEdit.setValidator(httpValidator)
        self.ui_WizardPage.apiUrlLineEdit.setValidator(httpValidator)
        self.ui_WizardPage.repoUrlLineEdit.setValidator(httpValidator)

        self.registerField(u"webUrl*", self.ui_WizardPage.webUrlLineEdit)
        self.registerField(u"apiUrl*", self.ui_WizardPage.apiUrlLineEdit)
        self.registerField(u"repoUrl*", self.ui_WizardPage.repoUrlLineEdit)
        self.registerField(u"username*", self.ui_WizardPage.usernameLineEdit)
        self.registerField(u"password*", self.ui_WizardPage.passwordLineEdit)

    def initializePage(self):
        super(ObsLightWizardPage, self).initializePage()
        self._clearEffects()

    def cleanupPage(self):
        pass

    def validatePage(self):
        self._clearEffects()
        self.setBusyCursor(self.doValidatePage)
        return self.isOk

    def _clearEffects(self):
        removeEffect(self.ui_WizardPage.apiUrlLineEdit)
        removeEffect(self.ui_WizardPage.repoUrlLineEdit)
        removeEffect(self.ui_WizardPage.webUrlLineEdit)

    @uiFriendly()
    def _friendlyTestUrl(self, url):
        return self.manager.testUrl(url)

    @uiFriendly()
    def _friendlyTestHost(self, url):
        return self.manager.testHost(url)

    @uiFriendly()
    def _friendlyTestApi(self, url, user, password):
        return self.manager.testApi(url, user, password)

    def doValidatePage(self):
        def testAndColorizeUrl(url, widget):
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
