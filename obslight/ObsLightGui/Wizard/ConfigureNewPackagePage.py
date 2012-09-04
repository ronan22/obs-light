# -*- coding: utf8 -*-
#
# Copyright 2012, Intel Inc.
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
Created on 17 avr. 2012

@author: Florent Vennetier
'''
from PySide.QtGui import QRegExpValidator

from WizardPageWrapper import ObsLightWizardPage
from ObsLightGui.Utils import PACKAGE_NAME_REGEXP

class ConfigureNewPackagePage(ObsLightWizardPage):

    def __init__(self, gui, index):
#        ObsLightWizardPage.__init__(self, gui, index, u"wizard_newPackage.ui")
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_newPackageFromGit.ui")
        packageNameValidator = QRegExpValidator(PACKAGE_NAME_REGEXP, self)
        self.ui_WizardPage.packageNameLineEdit.setValidator(packageNameValidator)
        self.registerField(u"newPackageName*",
                           self.ui_WizardPage.packageNameLineEdit)
        self.registerField(u"newPackageTitle",
                           self.ui_WizardPage.packageTitleLineEdit)
        self.registerField(u"newPackageDescription",
                           self.ui_WizardPage.packageDescriptionTextEdit)
        self.registerField(u"newPackageGitUrl",
                           self.ui_WizardPage.gitUrlLineEdit)

    def nextId(self):
        return -1

    def cleanupPage(self):
        pass

    def validatePage(self):
        newPkgName = self.field(u"newPackageName")
        newPkgTitle = self.field(u"newPackageTitle")
        newPkgDescr = self.field(u"newPackageDescription")
        projectAlias = self.field(u"projectAlias")
        newPkgGitUrl = self.field(u"newPackageGitUrl")
#        retVal = self._createPackage(projectAlias, newPkgName,
#                                     newPkgTitle, newPkgDescr)
        retVal = self._importPackageFromGit(projectAlias, newPkgName,
                                            newPkgTitle, newPkgDescr, newPkgGitUrl)
        return retVal is not None

    def _createPackage(self, project, name, title, description):
        retVal = self.callWithInfiniteProgress(self.manager.createLocalProjectObsPackage,
                                               "Creating package %s" % name,
                                               project,
                                               name,
                                               title,
                                               description)
        return retVal

    def _importPackageFromGit(self, project, name, title, description, url):
        retVal = self.callWithInfiniteProgress(self.manager.importPackage,
                                               "Creating package %s" % name,
                                               project,
                                               name,
                                               url)
        return retVal
