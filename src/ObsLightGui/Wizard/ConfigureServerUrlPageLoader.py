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
from PySide.QtGui import QLineEdit, QRegExpValidator

from WizardPageLoader import WizardPageLoader

class ConfigureServerUrlPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_configServerUrl.ui")
        webUrlLineEdit = self.page.findChild(QLineEdit, u"webUrlLineEdit")
        apiUrlLineEdit = self.page.findChild(QLineEdit, u"apiUrlLineEdit")
        repoUrlLineEdit = self.page.findChild(QLineEdit, u"repoUrlLineEdit")

        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp(u"http[s]?://.+"))
        webUrlLineEdit.setValidator(httpValidator)
        apiUrlLineEdit.setValidator(httpValidator)
        repoUrlLineEdit.setValidator(httpValidator)

        self.page.registerField(u"webUrl*", webUrlLineEdit)
        self.page.registerField(u"apiUrl*", apiUrlLineEdit)
        self.page.registerField(u"repoUrl*", repoUrlLineEdit)

        # does not work
        self.page.validatePage = self.validatePage

    def validatePage(self):
        print "validating..."
        return True
