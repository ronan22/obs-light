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
Created on 22 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import Qt

from ObsLightGui.Utils import uiFriendly, popupOnException

from WizardPageWrapper import ObsLightWizardPage

class ChoosePackagePage(ObsLightWizardPage):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_choosePackage.ui")
        self.registerField(u"packageRow*", self.ui_WizardPage.packageListWidget)
        self.ui_WizardPage.filterLineEdit.textEdited.connect(self.on_filterLineEdit_textEdited)
        self.setCommitPage(True)

    def initializePage(self):
        serverAlias = self.field(u"serverAlias")
        project = self.wizard().getSelectedProject()
        self.setBusyCursor(self._fillPackageList, serverAlias, project)

    @popupOnException
    def validatePage(self):
        if not self.isComplete():
            return False

        project = self.wizard().getSelectedProject()
        package = self.getSelectedPackage()
        self.setBusyCursor(self._addPackage, project, package)
        return True

    def _fillPackageList(self, serverAlias, project):
        self.ui_WizardPage.packageListWidget.clear()
        pkgList = self._getPackageList(serverAlias, project)
        self.ui_WizardPage.packageListWidget.addItems(pkgList)

    @uiFriendly()
    def _getPackageList(self, serverAlias, project):
        return self.manager.getObsProjectPackageList(serverAlias, project)

    @uiFriendly()
    def _addPackage(self, project, package):
        self.manager.addPackage(project, package)

    def on_filterLineEdit_textEdited(self, newFilter):
        for i in range(self.ui_WizardPage.packageListWidget.count()):
            item = self.ui_WizardPage.packageListWidget.item(i)
            item.setHidden(True)
        for item in self.ui_WizardPage.packageListWidget.findItems(newFilter, Qt.MatchContains):
            item.setHidden(False)

    def getSelectedPackage(self):
        return self.ui_WizardPage.packageListWidget.item(self.field(u"packageRow")).text()
