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
Created on 19 sept. 2012

@author: Ronan Le Martret
'''

from WizardPageWrapper import ObsLightWizardPage
from ObsLightGui.Utils import URL_REGEXP
from PySide.QtGui import QRegExpValidator

class ChooseRepositoryPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseRepository.ui")
        httpValidator = QRegExpValidator(URL_REGEXP, self)
        self.ui_WizardPage.lineEdit.setValidator(httpValidator)

        self.ui_WizardPage.AddRepositoryButton.clicked.connect(self.on_AddRepositoryButton_clicked)

        self.ui_WizardPage.autoAddRepoButton.stateChanged.connect(self._checkAutoAddRepoButton)

        self.__addedRepo = []
        self.__addLocalProject = True

    def initializePage(self):
        self.ui_WizardPage.autoAddRepoButton.setChecked (self.__addLocalProject)

        self.initializePage_RepoList()

    def _checkAutoAddRepoButton(self):
        self.__addLocalProject = self.ui_WizardPage.autoAddRepoButton.isChecked()

    def initializePage_RepoList(self):
        repoList = self.manager.getRepoFromGbsProjectConf(self.wizard().getProjectTemplatePath())
        repoList.extend(self.__addedRepo)
        repoList.sort()
        self.ui_WizardPage.RepoListWidget.clear()
        self.ui_WizardPage.RepoListWidget.addItems(repoList)

        self.ui_WizardPage.lineEdit.setText("http://")

    def on_AddRepositoryButton_clicked(self):
        addedRepo = self.ui_WizardPage.lineEdit.text()
        self.__addedRepo.append(addedRepo)
        self.initializePage()

    def nextId(self):
        return self.wizard().pageIndex(u'ChooseGbsArch')

    def getAddedRepo(self):
        return self.__addedRepo



