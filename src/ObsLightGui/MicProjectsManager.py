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

from PySide.QtGui import QFileDialog, QInputDialog, QMessageBox

from ObsLightGuiObject import ObsLightGuiObject
from ProjectsManagerBase import ProjectsManagerBase
from Utils import popupOnException
from MicProjectManager import MicProjectManager

class MicProjectsManager(ObsLightGuiObject, ProjectsManagerBase):

    __micProjects = {}

    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        ProjectsManagerBase.__init__(self,
                                     self.mainWindow.micProjectsListWidget,
                                     self.manager.getMicProjectList)
        self.__connectButtons()
        self.__connectEvents()
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
        self.mainWindow.newMicProjectButton.clicked.connect(self.on_newMicProjectButton_clicked)
        delClickSignal = self.mainWindow.deleteMicProjectButton.clicked
        delClickSignal.connect(self.on_deleteMicProjectButton_clicked)

    def __connectEvents(self):
        self.projectListWidget.currentTextChanged.connect(self.on_projectSelected)
        self.__connectProjectEvents()

    def __connectProjectEvents(self):
        imgTypeChanged = self.mainWindow.imageTypeComboBox.currentIndexChanged[unicode]
        imgTypeChanged.connect(self.on_imageTypeComboBox_currentIndexChanged)
        archChanged = self.mainWindow.architectureComboBox.currentIndexChanged[unicode]
        archChanged.connect(self.on_architectureComboBox_currentIndexChanged)

    def __diconnectProjectEvents(self):
        imgTypeChanged = self.mainWindow.imageTypeComboBox.currentIndexChanged[unicode]
        imgTypeChanged.disconnect(self.on_imageTypeComboBox_currentIndexChanged)
        archChanged = self.mainWindow.architectureComboBox.currentIndexChanged[unicode]
        archChanged.disconnect(self.on_architectureComboBox_currentIndexChanged)

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
# --- end Button handlers ----------------------------------------------------

# --- Event handlers ---------------------------------------------------------
    def on_projectSelected(self):
        """Called when user clicks on a project"""
        if self.currentProject is None:
            self.mainWindow.micProjectsTabWidget.setEnabled(False)
            return
        self.__diconnectProjectEvents()
        self.mainWindow.micProjectsTabWidget.setEnabled(True)
        self._currentProjectObj.refresh()
        self.__connectProjectEvents()

    def on_imageTypeComboBox_currentIndexChanged(self, imageType):
        """Called when user changes image type combo box"""
        self._currentProjectObj.imageType = imageType

    def on_architectureComboBox_currentIndexChanged(self, architecture):
        """Called when user changes architecture combo box"""
        self._currentProjectObj.architecture = architecture
# --- end Event handlers -----------------------------------------------------
