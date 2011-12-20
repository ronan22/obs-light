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

from PySide.QtCore import QRegExp, Qt
from PySide.QtGui import QLineEdit, QRegExpValidator

from ObsLightGui.Utils import colorizeWidget, removeEffect, isNonEmptyString, uiFriendly

from WizardPageLoader import WizardPageLoader

class ConfigureServerUrlPageLoader(WizardPageLoader):

    isOk = True

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_configServerUrl.ui")
        self.webUrlLineEdit = self.page.findChild(QLineEdit, u"webUrlLineEdit")
        self.apiUrlLineEdit = self.page.findChild(QLineEdit, u"apiUrlLineEdit")
        self.repoUrlLineEdit = self.page.findChild(QLineEdit, u"repoUrlLineEdit")
        self.userLineEdit = self.page.findChild(QLineEdit, u"usernameLineEdit")
        self.passLineEdit = self.page.findChild(QLineEdit, u"passwordLineEdit")
        self.isOk = True

        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp(u"http[s]?://.+"))
        self.webUrlLineEdit.setValidator(httpValidator)
        self.apiUrlLineEdit.setValidator(httpValidator)
        self.repoUrlLineEdit.setValidator(httpValidator)

        self.page.registerField(u"webUrl*", self.webUrlLineEdit)
        self.page.registerField(u"apiUrl*", self.apiUrlLineEdit)
        self.page.registerField(u"repoUrl*", self.repoUrlLineEdit)
        self.page.registerField(u"username*", self.userLineEdit)
        self.page.registerField(u"password*", self.passLineEdit)

        self.page.validatePage = self.beginValidatePage

    def _clearEffects(self):
        removeEffect(self.apiUrlLineEdit)
        removeEffect(self.repoUrlLineEdit)
        removeEffect(self.webUrlLineEdit)

    @uiFriendly
    def _friendlyTestUrl(self, url):
        return self.manager.testUrl(url)

    @uiFriendly
    def _friendlyTestHost(self, url):
        return self.manager.testHost(url)

    @uiFriendly
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
            except BaseException:
                pass
            finally:
                colorizeWidget(widget, color)
            return isOk

        def testAndColorizeString(theString, widget):
            isOk = isNonEmptyString(theString)
            colorizeWidget(widget, "green" if isOk else "red")
            return isOk

        web = self.page.field(u"webUrl")
        api = self.page.field(u"apiUrl")
        repo = self.page.field(u"repoUrl")
        user = self.page.field(u"username")
        password = self.page.field(u"password")

        userPassOk = testAndColorizeString(user, self.userLineEdit)
        userPassOk = testAndColorizeString(password, self.passLineEdit) and userPassOk

        allOk = userPassOk
        allOk = testAndColorizeUrl(web, self.webUrlLineEdit) and allOk
        allOk = testAndColorizeUrl(repo, self.repoUrlLineEdit) and allOk

        if userPassOk:
            apiRes = self._friendlyTestApi(api, user, password)
            if apiRes == 1:
                colorizeWidget(self.userLineEdit, "red")
                colorizeWidget(self.passLineEdit, "red")
                allOk = False
            elif apiRes == 2:
                colorizeWidget(self.apiUrlLineEdit, "red")
                colorizeWidget(self.userLineEdit, "orange")
                colorizeWidget(self.passLineEdit, "orange")
                allOk = False
            else:
                colorizeWidget(self.apiUrlLineEdit, "green")
                colorizeWidget(self.userLineEdit, "green")
                colorizeWidget(self.passLineEdit, "green")

        self.isOk = allOk

    def beginValidatePage(self):
        self._clearEffects()
        oldCursor = self.page.wizard().cursor()
        self.page.wizard().setCursor(Qt.WaitCursor)
        self.page.setEnabled(False)
        self.doValidatePage()
        self.page.setEnabled(True)
        self.page.wizard().setCursor(oldCursor)
        return self.isOk
