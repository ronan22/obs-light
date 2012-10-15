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
from PySide.QtGui import QStandardItemModel, QStandardItem, QCheckBox
from PySide.QtCore import QAbstractListModel, Qt, QAbstractItemModel, QAbstractTableModel, QSize

from ObsLightGui.Utils import URL_REGEXP
from PySide.QtGui import QRegExpValidator

class RepoModel(QAbstractTableModel):
    def __init__(self, repoTuple):
        QAbstractTableModel.__init__(self)

        self._repoTuple = repoTuple

    #model
    def rowCount(self, _parent=None):
        return len(self._repoTuple)

    #model
    def columnCount(self, _parent=None):
        return 2

    #model
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index.row(), index.column())
#        elif role == Qt.ForegroundRole:
#            return self.foregroundRoleData(index)
#        elif role == Qt.TextAlignmentRole:
#            return self.textAlignmentRoleData(index)
        return None
    #model
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == 0:
                    return "Name"
                else:
                    return "URL"
        elif role == Qt.SizeHintRole:
#            if orientation == Qt.Orientation.Vertical:
#                pass
#            else:
            if section == 1:
                return QSize(0, 0)
#            elif section == 2:
#                return QSize(320, 0)
        return None

    def displayRoleData(self, row, column):
        rName, rUrl = self._repoTuple[row]
        if column == 0:
            return rName
        else:

            return rUrl

#    def foregroundRoleData(self, index):
#        row = index.row()
#        column = index.column()
#        drData = self.displayRoleData(row, column)
#
#        color = self.colors[column].get(drData, None)
#        return color

#    def textAlignmentRoleData(self, index):
#        column = index.column()
#        if column in range(1, self.columnCount()):
#            return Qt.AlignCenter
##            return Qt.AlignHCenter | Qt.AlignVCenter
#        else:
#            return Qt.AlignVCenter


#    def sort(self, Ncol, order):
#        print "Sort data according to column ", Ncol

    def refresh(self):
        self.resetCache()
        self.layoutChanged.emit()

    def getAddedRepo(self):
        return self._repoTuple

class ChooseRepositoryPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseRepository.ui")
        httpValidator = QRegExpValidator(URL_REGEXP, self)
        self.ui_WizardPage.repositoryUrlEdit.setValidator(httpValidator)

        self.ui_WizardPage.AddRepositoryButton.clicked.connect(self.on_AddRepositoryButton_clicked)
        self.ui_WizardPage.DelRepositoryButton.clicked.connect(self.on_DelRepositoryButton_clicked)

#        self.ui_WizardPage.autoAddRepoButton.stateChanged.connect(self._checkAutoAddRepoButton)

        self.__repoList = []
        self.__addLocalProject = True

    def initializePage(self):
#        self.ui_WizardPage.autoAddRepoButton.setChecked(self.__addLocalProject)
        self.__repoList = self.wizard().getInitProjectRepo()
        self.initializePage_RepoList()

#    def _checkAutoAddRepoButton(self):
#        self.__addLocalProject = self.ui_WizardPage.autoAddRepoButton.isChecked()

    def initializePage_RepoList(self):
        self.__repoModel = RepoModel(self.__repoList)

        self.ui_WizardPage.RepoTableView.setModel(self.__repoModel)
        self.ui_WizardPage.RepoTableView.setEnabled (True)
        self.ui_WizardPage.RepoTableView.resizeColumnToContents(0)
        self.ui_WizardPage.RepoTableView.resizeColumnToContents(1)
        self.ui_WizardPage.repositoryUrlEdit.setText("http://")

    def on_AddRepositoryButton_clicked(self):
        repoName = self.ui_WizardPage.repositoryNameEdit.text()
        repoUrl = self.ui_WizardPage.repositoryUrlEdit.text()
        self.__repoList.append((repoName, repoUrl))
        self.initializePage_RepoList()

    def on_DelRepositoryButton_clicked(self):
        row = self.ui_WizardPage.RepoTableView.currentIndex().row()
        if 0 <= row <= len(self.__repoList):
            self.__repoList.pop(row)
        self.initializePage_RepoList()

    def nextId(self):
        return self.wizard().pageIndex(u'ChooseGbsArch')

    def getAddedRepo(self):
        return self.__repoModel.getAddedRepo()

    def autoAddProjectRepo(self):
        return self.__addLocalProject

