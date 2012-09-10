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
Created on 05 sept. 2012

@author: Ronan Le Martret
'''
from PySide.QtGui import QMessageBox

from ObsLightGui.FilterableWidget import FilterableWidget
from ObsLightGui.Utils import popupOnException, firstArgLast
from WizardPageWrapper import ObsLightWizardPage

class ChooseLocalPackagePage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseLocalPackage.ui")
        FilterableWidget.__init__(self, self.ui_WizardPage.filterLineEdit,
                                  self.ui_WizardPage.packageListWidget,
                                  multiSelection=True)
        self.registerField(u"localPackageRow", self.ui_WizardPage.packageListWidget)


        self.setCommitPage(True)

    def initializePage(self):
        project = self.wizard().getSelectedLocalProject()

        pkgList = self.manager.getLocalProjectPackageList(project, onlyInstalled=True)

        # if _getPackageList gets an exception, it is caught by
        # callWithInfiniteProgress, and None is returned.
        if pkgList is not None:
            self.ui_WizardPage.packageListWidget.addItems(pkgList)

    @popupOnException
    def validatePage(self):
        if not self.isComplete():
            return False
        projectSrc = self.wizard().getSelectedLocalProject()
        projectDst = self.field(u"projectAlias")
        packages = self.getSelectedPackages()

        listPackageRemote = set(self.manager.getLocalProjectPackageList(projectDst, onlyInstalled=True))
        listPackageLocal = set(self.manager.getLocalProjectPackageList(projectDst, onlyInstalled=False))

        interPackage = packages.intersection(listPackageRemote.union(listPackageLocal))

        if len(interPackage) > 0:
            msg = u"Warning: the packages '%s' from %s you selected is already exist in project %s.\n"
            msg = msg % (" ,".join(interPackage), projectSrc, projectDst)
            msg += u"The copy will overwrite the %s packages .\n\n" % projectDst
            msg += u"Do you want to copy it anyway?"
            result = QMessageBox.warning(self,
                                         u"Copy Local package.",
                                         msg,
                                         buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                         defaultButton=QMessageBox.Yes)
            if result == QMessageBox.Cancel:
                return False
        self._copyPackages(projectSrc, projectDst, packages)
        return True

    def getSelectedPackages(self):
        items = self.ui_WizardPage.packageListWidget.selectedItems()
        packages = set()
        for item in items:
            packageName = item.text()
            packages.add(packageName)
        return packages

    def _copyPackages(self, projectSrc, projectDst, packages):
        swappedAddPackage = firstArgLast(self.manager.localCopyPackage)
        self.callWithProgress(swappedAddPackage,
                              packages,
                              u"Adding package %(arg)s...",
                              projectSrc,
                              projectDst)

    def nextId(self):
        return -1
