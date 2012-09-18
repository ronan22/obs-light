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
Created on 17 sept. 2012

@author: ronan Le Martret
'''

from WizardPageWrapper import ObsLightWizardPage
from PySide.QtGui import QFileDialog

from PySide.QtGui import QStandardItemModel, QStandardItem, QCheckBox
from PySide.QtCore import QAbstractListModel, Qt, QAbstractItemModel

class ItemTree(object):
    '''
    abstract class used for package and project colection.
    '''
    def __init__(self, name=None):
        self.name = name
        self.checked = False

    def toggleCheckedValue(self):
        self.checked = not self.checked

class PackageGit(ItemTree):
    '''
    Package is define by a name, a status(check/uncheck),a git URL.
    '''
    def __init__(self, name=None, gitUrl=None):
        ItemTree.__init__(self, name)
        self.gitUrl = gitUrl

class ProjectGit(ItemTree):
    '''
    Project is define by a name, a status(check/uncheck),
    a collection of sub project,
    a collection of package.
    '''
    def __init__(self, name=None):
        ItemTree.__init__(self, name)

        self.__projectList = []
        self.__packageList = []
        self.__projectGitDict = {}

    def addPackage(self, projectNameList, package, gitUrl):
        '''
        'projectNameList' is a list of project, the first element of 'projectNameList' is the direct,
        sub project of the current directory.
        if the projectNameList is empty, the define package is add to the current package.
        else 
        '''
        if len(projectNameList) == 0:
            self.__packageList.append(PackageGit(package, gitUrl))
            self.__packageList.sort()
        else:
            projectName = projectNameList[0]
            if projectName not in self.__projectList:
                self.__addProject(projectName)

            self.__projectGitDict[projectName].addPackage(projectNameList[1:], package, gitUrl)

    def __addProject(self, projectName):
        '''
        add a sub project 'projectName'
        '''
        self.__projectList.append(projectName)
        self.__projectList.sort()
        self.__projectGitDict[projectName] = ProjectGit(projectName)

    def getTree(self):
        '''
        return a list of project and package (sorted).
        '''
        rowItems = list()
        for project in self.__projectList :
            projectCollection = self.__projectGitDict[project]
            projectTree = QStandardItem(projectCollection.name)
            for t in projectCollection.getTree():
                projectTree.appendRow(t)

            rowItems.append(projectTree)

        for package in self.__packageList:
            rowItems.append(QStandardItem(package.name))

        return rowItems

    def getItem(self, listParent):
        '''
        return a item element (project or package)
        '''
        if len(listParent) == 0:
            return self

        elif len(listParent) == 1:
            index = listParent[0]
            nbProject = len(self.__projectList)
            if index < nbProject:
                project = self.__projectList[index]
                return self.__projectGitDict[project]
            else:
                index = index - nbProject
                return self.__packageList[index]
        else:
            index = listParent[0]
            nbProject = len(self.__projectList)
            project = self.__projectList[index]
            return self.__projectGitDict[project].getItem(listParent[1:])

    def setCheckedValue(self, val):
        '''
        Set the check Value, the fonction set all package and sub project to the same value
        '''
        self.checked = val
        for project in self.__projectList :
            self.__projectGitDict[project].setCheckedValue(val)

        for package in self.__packageList:
            package.checked = val

    def toggleCheckedValue(self):
        '''
        if the checked is False, it ll be set to True, vice-versa. 
        set all package and sub project to the same value.
        '''
        ItemTree.toggleCheckedValue(self)
        self.setCheckedValue(self.checked)

    def getSelected(self):
        '''
        return the package whose check is True
        '''
        res = []
        for project in self.__projectList :
            res.extend(self.__projectGitDict[project].getSelected())

        for package in self.__packageList:
            if package.checked:
                res.append((package.name, package.gitUrl))
        return res


class ProjectGitCollection:

    def __init__(self):
        f = open("/home/meego/Documents/Tizen/TizenScript/resultPackage.sav", "r")

        self.__projectGitCollection = ProjectGit()

        for line in f:
            project , package , git = line.split()
            self.__projectGitCollection.addPackage(project.split("/"), package, git)
        f.close()

    def createTree(self, item):
        for t in self.__projectGitCollection.getTree():
            item.appendRow(t)

    def getCheckedValue(self, listParent):
        listParent.reverse()
        return self.__projectGitCollection.getItem(listParent).checked

    def getName(self, listParent):
        listParent.reverse()
        return self.__projectGitCollection.getItem(listParent).name

    def toggleCheckedValue(self, listParent):
        listParent.reverse()
        item = self.__projectGitCollection.getItem(listParent)
        item.toggleCheckedValue()

    def unselectAll(self):
        self.__projectGitCollection.setCheckedValue(False)

    def selectAll(self):
        self.__projectGitCollection.setCheckedValue(True)

    def getSelected(self):
        return self.__projectGitCollection.getSelected()

class chooseGitPackageModel(QStandardItemModel):
    def __init__(self):
        QStandardItemModel.__init__(self)

        self.item = self.invisibleRootItem()
        self.item.setEnabled(True)

        self.__projectGitCollection = ProjectGitCollection()
        self.__projectGitCollection.createTree(self.item)

    def getCollection(self):
        return self.__projectGitCollection

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "package"
                else:
                    return ""

    def flags(self, index):
        superFlags = super(QStandardItemModel, self).flags(index)

        superFlags = superFlags | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

        return superFlags

    def __getIndexList(self, index):
        listParent = []
        parentIndex = index
        while parentIndex.isValid ():
            listParent.append(parentIndex.row())
            parentIndex = parentIndex.parent()

        return listParent

    def data(self, index, role=Qt.DisplayRole):
        listParent = self.__getIndexList(index)

        if role == Qt.DisplayRole:
            return self.__projectGitCollection.getName(listParent)

        if role == Qt.CheckStateRole :
            checkedValue = self.__projectGitCollection.getCheckedValue(listParent)

            if checkedValue:
                return Qt.Checked
            else:
                return Qt.Unchecked

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole :
            listParent = self.__getIndexList(index)
            self.__projectGitCollection.toggleCheckedValue(listParent)
            self.layoutChanged.emit()
        return True

class ConfigureGitProjectPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseGitProject.ui")

        self.ui_WizardPage.updateListPushButton.clicked.connect(self.on_updateListPushButton_clicked)
        self.ui_WizardPage.loadManifestPushButton.clicked.connect(self.on_loadManifestPushButton_clicked)
        self.ui_WizardPage.selectAllPushButton.clicked.connect(self.on_selectAllPushButton_clicked)
        self.ui_WizardPage.unselectAllPushButton.clicked.connect(self.on_unselectAllPushButton_clicked)
        self.ui_WizardPage.importPushButton.clicked.connect(self.on_importPushButton_clicked)

        self.__gitProjectTreeView = self.ui_WizardPage.gitProjectTreeView
        self.__initViewTree()

    def __initViewTree(self):

        self.standardModel = chooseGitPackageModel()
        self.__gitProjectTreeView.setModel(self.standardModel)
        self.__gitProjectTreeView.collapseAll()

    def cleanupPage(self):
        pass

    def nextId(self):
        return -1

    def on_updateListPushButton_clicked(self):
        print "update"

    def on_loadManifestPushButton_clicked(self):
        filters = "manifest files (*.xml);;All files (*)"
        filePath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        "Select manifest file (*.xml) to import",
                                                        filter=filters)
        if len(filePath) < 1:
            return
        print "filePath, _filter", filePath, _filter

    def on_selectAllPushButton_clicked(self):
        self.standardModel.getCollection().selectAll()
        self.standardModel.layoutChanged.emit()

    def on_unselectAllPushButton_clicked(self):
        self.standardModel.getCollection().unselectAll()
        self.standardModel.layoutChanged.emit()

    def on_importPushButton_clicked(self):
        res = self.standardModel.getCollection().getSelected()
        for p, g in res:
            print "package", p.ljust(25), " git:", g










