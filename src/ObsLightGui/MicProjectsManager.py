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

class MicProjectsManager(ObsLightGuiObject, ProjectsManagerBase):
    def __init__(self, gui):
        ObsLightGuiObject.__init__(self, gui)
        ProjectsManagerBase.__init__(self,
                                     self.mainWindow.micProjectsListWidget,
                                     self.manager.getMicProjectList)
        self.__connectButtons()
        self.loadProjectList()

    def __connectButtons(self):
        self.mainWindow.importKickstartButton.clicked.connect(self.on_importKickstartButton_clicked)
        self.mainWindow.newMicProjectButton.clicked.connect(self.on_newMicProjectButton_clicked)
        delClickSignal = self.mainWindow.deleteMicProjectButton.clicked
        delClickSignal.connect(self.on_deleteMicProjectButton_clicked)

# --- Button handlers --------------------------------------------------------
    @popupOnException
    def on_importKickstartButton_clicked(self):
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
        self.refresh()
# --- end Button handlers ----------------------------------------------------
