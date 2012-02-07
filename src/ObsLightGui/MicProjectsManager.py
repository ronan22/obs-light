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
Created on 2 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtGui import QFileDialog, QInputDialog, QMessageBox, QTableView

from ObsLightGuiObject import ObsLightGuiObject
from ProjectsManagerBase import ProjectsManagerBase
from Utils import getSelectedRows, popupOnException
from MicProjectManager import MicProjectManager

class MicProjectsManager(ObsLightGuiObject, ProjectsManagerBase):

    __micProjects = {}
    __configDialog = None

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        ProjectsManagerBase.__init__(self,
                                     self.mainWindow.micProjectsListWidget,
                                     self.manager.getMicProjectList)
        self.__connectButtons()
        self.__connectEvents()
        self.mainWindow.kickstartRepositoriesTableView.setSelectionBehavior(QTableView.SelectRows)
        self.mainWindow.kickstartPackagesTableView.setSelectionBehavior(QTableView.SelectRows)
        self.mainWindow.kickstartPackageGroupsTableView.setSelectionBehavior(QTableView.SelectRows)
        self.loadProjectList()

    @property
    def _currentProjectObj(self):
        """
        Get the MicProjectManager object of the current project.
        """
        if not self.currentProject in self.__micProjects:
            self.__micProjects[self.currentProject] = MicProjectManager(self.gui,
                                                                        self.currentProject)
        return self.__micProjects[self.currentProject]

    def __connectButtons(self):
        self.mainWindow.importKickstartButton.clicked.connect(self.on_importKickstartButton_clicked)
        self.mainWindow.exportKickstartButton.clicked.connect(self.on_exportKickstartButton_clicked)
        self.mainWindow.newMicProjectButton.clicked.connect(self.on_newMicProjectButton_clicked)
        delClickSignal = self.mainWindow.deleteMicProjectButton.clicked
        delClickSignal.connect(self.on_deleteMicProjectButton_clicked)

    def __connectEvents(self):
        self.projectListWidget.currentTextChanged.connect(self.on_projectSelected)
        self.__connectProjectEventsAndButtons()

    def __connectProjectEventsAndButtons(self):
        imgTypeChanged = self.mainWindow.imageTypeComboBox.currentIndexChanged[unicode]
        imgTypeChanged.connect(self.on_imageTypeComboBox_currentIndexChanged)
        archChanged = self.mainWindow.architectureComboBox.currentIndexChanged[unicode]
        archChanged.connect(self.on_architectureComboBox_currentIndexChanged)
        createImageClicked = self.mainWindow.createImageButton.clicked
        createImageClicked.connect(self.on_createImageButton_clicked)
        removeRepoClicked = self.mainWindow.removeRepositoryButton.clicked
        removeRepoClicked.connect(self.on_removeRepositoryButton_clicked)
        addRepoClicked = self.mainWindow.addRepositoryButton.clicked
        addRepoClicked.connect(self.on_addRepositoryButton_clicked)
        addRepo2Clicked = self.mainWindow.addRepositoryFromProjectButton.clicked
        addRepo2Clicked.connect(self.on_addRepositoryFromProjectButton_clicked)
        addPkgClicked = self.mainWindow.addPackageButton.clicked
        addPkgClicked.connect(self.on_addPackageButton_clicked)
        removePkgClicked = self.mainWindow.removePackageButton.clicked
        removePkgClicked.connect(self.on_removePackageButton_clicked)
        addPkgGrpClicked = self.mainWindow.addPackageGroupButton.clicked
        addPkgGrpClicked.connect(self.on_addPackageGroupButton_clicked)
        removePkgGrpClicked = self.mainWindow.removePackageGroupButton.clicked
        removePkgGrpClicked.connect(self.on_removePackageGroupButton_clicked)

    def __disconnectProjectEventsAndButtons(self):
        imgTypeChanged = self.mainWindow.imageTypeComboBox.currentIndexChanged[unicode]
        imgTypeChanged.disconnect(self.on_imageTypeComboBox_currentIndexChanged)
        archChanged = self.mainWindow.architectureComboBox.currentIndexChanged[unicode]
        archChanged.disconnect(self.on_architectureComboBox_currentIndexChanged)
        createImageClicked = self.mainWindow.createImageButton.clicked
        createImageClicked.disconnect(self.on_createImageButton_clicked)
        removeRepoClicked = self.mainWindow.removeRepositoryButton.clicked
        removeRepoClicked.disconnect(self.on_removeRepositoryButton_clicked)
        addRepoClicked = self.mainWindow.addRepositoryButton.clicked
        addRepoClicked.disconnect(self.on_addRepositoryButton_clicked)
        addRepo2Clicked = self.mainWindow.addRepositoryFromProjectButton.clicked
        addRepo2Clicked.disconnect(self.on_addRepositoryFromProjectButton_clicked)
        addPkgClicked = self.mainWindow.addPackageButton.clicked
        addPkgClicked.disconnect(self.on_addPackageButton_clicked)
        removePkgClicked = self.mainWindow.removePackageButton.clicked
        removePkgClicked.disconnect(self.on_removePackageButton_clicked)
        addPkgGrpClicked = self.mainWindow.addPackageGroupButton.clicked
        addPkgGrpClicked.disconnect(self.on_addPackageGroupButton_clicked)
        removePkgGrpClicked = self.mainWindow.removePackageGroupButton.clicked
        removePkgGrpClicked.disconnect(self.on_removePackageGroupButton_clicked)

# --- Button handlers --------------------------------------------------------
    @popupOnException
    def on_importKickstartButton_clicked(self):
        """Called when user clicks on 'import kickstart'"""
        micProject = self.currentProject
        if micProject is None:
            return
        filters = "Kickstart files (*.ks);;All files (*)"
        filePath, _filter = QFileDialog.getOpenFileName(self.mainWindow,
                                                        "Select kickstart file to import",
                                                        filter=filters)
        if len(filePath) < 1:
            return
        self.callWithInfiniteProgress(self.manager.setKickstartFile,
                                      "Importing Kickstart file",
                                      micProject,
                                      filePath)

    @popupOnException
    def on_exportKickstartButton_clicked(self):
        """Called when user clicks on 'export kickstart'"""
        if self.currentProject is None:
            return
        filters = "Kickstart files (*.ks);;All files (*)"
        filePath, _filter = QFileDialog.getSaveFileName(self.mainWindow,
                                                        "Select the file to export kickstart to",
                                                        filter=filters)
        if len(filePath) < 1:
            return
        self.callWithInfiniteProgress(self.manager.saveKickstartFile,
                                      "Exporting Kickstart file",
                                      self.currentProject,
                                      filePath)

    @popupOnException
    def on_newMicProjectButton_clicked(self):
        """Called when user clicks on 'new project'"""
        name, accepted = QInputDialog.getText(self.mainWindow,
                                              "New MIC project",
                                              "Select a name for the new project:")
        if not accepted or len(name) < 1:
            return
        self.callWithInfiniteProgress(self.manager.addMicProject,
                                      "Creating MIC project",
                                      name)
        self.refresh()

    @popupOnException
    def on_deleteMicProjectButton_clicked(self):
        """Called when user clicks on 'delete project'"""
        micProject = self.currentProject
        if micProject is None:
            return
        result = QMessageBox.question(self.mainWindow,
                                      u"Are you sure ?",
                                      u"Are you sure you want to delete %s project ?"
                                        % micProject,
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        self.callWithInfiniteProgress(self.manager.deleteMicProject,
                                      "Deleting MIC project",
                                      micProject)
        self.__micProjects.pop(micProject, None)
        self.refresh()

    @popupOnException
    def on_createImageButton_clicked(self):
        """Called when user clicks on 'create image'"""
        micProject = self.currentProject
        if micProject is None:
            return
        self._currentProjectObj.createImage()

    @popupOnException
    def on_removeRepositoryButton_clicked(self):
        """Called when user clicks on 'remove repository'"""
        repositories = []
        for row in getSelectedRows(self.mainWindow.kickstartRepositoriesTableView):
            repo = self._currentProjectObj.getRepositoryNameByRowId(row)
            if repo is not None:
                repositories.append(repo)
        if len(repositories) < 1:
            return
        result = QMessageBox.question(self.mainWindow,
                                      u"Are you sure ?",
                                      u"Are you sure you want to remove %d repositories ?"
                                        % len(repositories),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        for repo in repositories:
            self._currentProjectObj.removeRepository(repo)

    @popupOnException
    def on_addRepositoryButton_clicked(self):
        """Called when user clicks on 'add repository'"""
        self.__configDialog = self.gui.loadWindow(u"obsRepoConfig.ui")
        self.__configDialog.accepted.connect(self.on_configDialog_accepted)
        self.__configDialog.checkButton.hide()
        self.__configDialog.show()

    @popupOnException
    def on_addRepositoryFromProjectButton_clicked(self):
        projects = self.manager.getLocalProjectList()
        selectedProject, accepted = QInputDialog.getItem(self.mainWindow,
                                                         "Select project",
                                                         "Project to import repository from:",
                                                         projects,
                                                         editable=False)
        if not accepted:
            return
        repoUrl = self.callWithInfiniteProgress(self.manager.getProjectRepository,
                                                "Retrieving repository URL...",
                                                selectedProject)
        self._currentProjectObj.addRepository(selectedProject, repoUrl)

    @popupOnException
    def on_addPackageButton_clicked(self):
        selectedPackage, accepted = QInputDialog.getText(self.mainWindow,
                                                         "Select package",
                                                         "Enter a package name:")
        if not accepted or len(selectedPackage) < 1:
            return
        self._currentProjectObj.addPackage(selectedPackage)

    @popupOnException
    def on_removePackageButton_clicked(self):
        packages = []
        for row in getSelectedRows(self.mainWindow.kickstartPackagesTableView):
            package = self._currentProjectObj.getPackageNameByRowId(row)
            if package is not None:
                packages.append(package)
        if len(packages) < 1:
            return
        result = QMessageBox.question(self.mainWindow,
                                      u"Are you sure ?",
                                      u"Are you sure you want to remove %d packages ?"
                                        % len(packages),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        # removePackage supports lists
        self._currentProjectObj.removePackage(packages)

    def on_addPackageGroupButton_clicked(self):
        selectedPackageGroup, accepted = QInputDialog.getText(self.mainWindow,
                                                              "Select package group",
                                                              "Enter a package group name:")
        if not accepted or len(selectedPackageGroup) < 1:
            return
        self._currentProjectObj.addPackageGroup(selectedPackageGroup)

    def on_removePackageGroupButton_clicked(self):
        packageGroups = []
        for row in getSelectedRows(self.mainWindow.kickstartPackageGroupsTableView):
            group = self._currentProjectObj.getPackageGroupNameByRowId(row)
            if group is not None:
                packageGroups.append(group)
        if len(packageGroups) < 1:
            return
        result = QMessageBox.question(self.mainWindow,
                                      u"Are you sure ?",
                                      u"Are you sure you want to remove %d package groups ?"
                                        % len(packageGroups),
                                      buttons=QMessageBox.Yes | QMessageBox.No,
                                      defaultButton=QMessageBox.Yes)
        if result == QMessageBox.No:
            return
        # removePackageGroup supports lists
        self._currentProjectObj.removePackageGroup(packageGroups)
# --- end Button handlers ----------------------------------------------------

# --- Event handlers ---------------------------------------------------------
    def on_projectSelected(self):
        """Called when user clicks on a project"""
        if self.currentProject is None:
            self.mainWindow.micProjectsTabWidget.setEnabled(False)
            return
        self.__disconnectProjectEventsAndButtons()
        self.mainWindow.micProjectsTabWidget.setEnabled(True)
        self._currentProjectObj.refresh()
        self.__connectProjectEventsAndButtons()

    def on_imageTypeComboBox_currentIndexChanged(self, imageType):
        """Called when user changes image type combo box"""
        self._currentProjectObj.imageType = imageType

    def on_architectureComboBox_currentIndexChanged(self, architecture):
        """Called when user changes architecture combo box"""
        self._currentProjectObj.architecture = architecture

    @popupOnException
    def on_configDialog_accepted(self):
        """Called when user accepts repository configuration dialog"""
        name = self.__configDialog.repoAliasLineEdit.text()
        url = self.__configDialog.repoUrlLineEdit.text()
        self._currentProjectObj.addRepository(name, url)
# --- end Event handlers -----------------------------------------------------
