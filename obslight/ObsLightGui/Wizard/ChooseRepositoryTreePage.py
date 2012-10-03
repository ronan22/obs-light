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
Created on 25 sept. 2012

@author: Ronan Le Martret
'''

from WizardPageWrapper import ObsLightWizardPage

from PySide.QtGui import QStandardItemModel, QStandardItem, QCheckBox
from PySide.QtCore import QAbstractListModel, Qt, QAbstractItemModel

class chooseRepoModel(QStandardItemModel):
    def __init__(self, repoDict):
        QStandardItemModel.__init__(self)

        self.item = self.invisibleRootItem()
        self.item.setEnabled(True)

        self.__repoDict = repoDict
        self.__profileList = self.__repoDict.keys()
        self.__profileList.sort()

        if "general" in self.__profileList:
            self.__selectedRepo = "general"
        else:
            if len(self.__profileList) > 0:
                self.__selectedRepo = self.__profileList[0]

        for p in self.__profileList:
            profile = QStandardItem(p)
            for rName, rUrl in self.__repoDict[p]:
                st = rName + " (" + rUrl + ")"
                profile.appendRow(QStandardItem(st))
            self.item.appendRow(profile)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "profile"

    def flags(self, index):
        superFlags = super(QStandardItemModel, self).flags(index)
        superFlags = superFlags | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        return superFlags

    def data(self, index, role=Qt.DisplayRole):
        parentIndex = index.parent()

        if role == Qt.DisplayRole:
            if parentIndex.isValid ():
                profile = self.__profileList[parentIndex.row()]
                rName, rUrl = self.__repoDict[profile][index.row()]
                return rName + " (" + rUrl + ")"
            else:
                return self.__profileList[index.row()]

        if role == Qt.CheckStateRole:
            if parentIndex.isValid ():
                profile = self.__profileList[parentIndex.row()]

            else:
                profile = self.__profileList[index.row()]

            if (self.__selectedRepo == profile):
                return Qt.Checked
            else:
                return Qt.Unchecked

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole :
            parentIndex = index.parent()
            if not parentIndex.isValid ():
                self.__selectedRepo = self.__profileList[index.row()]
            self.layoutChanged.emit()
        return True

    def getInitProjectRepo(self):
        if self.__selectedRepo is None:
            return []
        else:
            return self.__repoDict[self.__selectedRepo]

    def getSelectedProjectRepo(self):
        return self.__selectedRepo

class ChooseRepositoryTreePage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseRepositoryTree.ui")
        self.__repositoryTreeView = self.ui_WizardPage.repositoryTreeView
        self.standardModel = None
        self.__selectedBuildConf = None

    def initializePage(self):
        repoDict = self.manager.getRepoFromGbsProjectConf(self.wizard().getProjectTemplatePath())

        self.standardModel = chooseRepoModel(repoDict)
        self.__repositoryTreeView.setModel(self.standardModel)
        self.__repositoryTreeView.collapseAll()

    def haveABuildConf(self):
        selectedProjectRepo = self.standardModel.getSelectedProjectRepo()
        selectedProjectConf = self.wizard().getProjectTemplatePath()
        self.__selectedBuildConf = self.manager.getBuildConfFromGbsProjectConf(selectedProjectRepo, selectedProjectConf)

        self.wizard().setSelectedBuildConf(self.__selectedBuildConf)

        return self.__selectedBuildConf is not None

    def nextId(self):
        if self.haveABuildConf():
            return self.wizard().pageIndex(u"ChooseRepository")
        else:
            return self.wizard().pageIndex(u"ChooseProjectConf")

    def getInitProjectRepo(self):
        if self.standardModel is None:
            return []
        else:
            return self.standardModel.getInitProjectRepo()


