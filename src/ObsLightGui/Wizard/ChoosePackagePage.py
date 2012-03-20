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

from ObsLightGui.FilterableWidget import FilterableWidget

from ObsLightGui.Utils import popupOnException, firstArgLast

from WizardPageWrapper import ObsLightWizardPage

class ChoosePackagePage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_choosePackage.ui")
        FilterableWidget.__init__(self, self.ui_WizardPage.filterLineEdit,
                                  self.ui_WizardPage.packageListWidget,
                                  multiSelection=True)
        self.registerField(u"packageRow*", self.ui_WizardPage.packageListWidget)
        self.setCommitPage(True)

    def initializePage(self):
        projectAlias = self.wizard().getSelectedProjectAlias()
        self.setBusyCursor(self._fillPackageList, projectAlias)

    @popupOnException
    def validatePage(self):
        if not self.isComplete():
            return False

        projectAlias = self.wizard().getSelectedProjectAlias()
        packages = self.getSelectedPackages()
        self._addPackages(projectAlias, packages)
        return True

    def _fillPackageList(self, projectAlias):
        self.ui_WizardPage.packageListWidget.clear()
        pkgList = self.callWithInfiniteProgress(self._getPackageList,
                                                u"Loading package list...",
                                                projectAlias)
        self.ui_WizardPage.packageListWidget.addItems(pkgList)

    def _getPackageList(self, projectAlias):
        return self.manager.getLocalProjectPackageList(projectAlias, onlyInstalled=False)

    def _addPackages(self, project, packages):
        swappedAddPackage = firstArgLast(self.manager.addPackage)
        self.callWithProgress(swappedAddPackage,
                              packages,
                              u"Adding package %(arg)s...",
                              project)

    def getSelectedPackage(self):
        return self.ui_WizardPage.packageListWidget.item(self.field(u"packageRow")).text()

    def getSelectedPackages(self):
        items = self.ui_WizardPage.packageListWidget.selectedItems()
        packages = set()
        for item in items:
            packageName = item.text()
            packages.add(packageName)
        return list(packages)
