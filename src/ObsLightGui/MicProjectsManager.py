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
Created on 2 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Qt

from ObsLightGuiObject import ObsLightGuiObject

# TODO: make a common parent class for MicProjectsManager and ProjectManager
#       with getCurrentProjectName, setCurrentProject, loadProjectList, refresh...
class MicProjectsManager(QObject, ObsLightGuiObject):
    def __init__(self, gui):
        QObject.__init__(self)
        ObsLightGuiObject.__init__(self, gui)
        self.loadProjectList()

    def loadProjectList(self):
        '''
        Load (or reload) the MIC project list.
        '''
        lastCurrentProject = self.getCurrentProjectName()
        projectList = self.manager.getMicProjectList()
        self.mainWindow.micProjectsListWidget.clear()
        self.mainWindow.micProjectsListWidget.addItems(projectList)
        if lastCurrentProject is not None and lastCurrentProject in projectList:
            self.setCurrentProject(lastCurrentProject)

    def getCurrentProjectName(self):
        '''
        Get the name of the project selected in the UI, or None.
        '''
        item = self.mainWindow.micProjectsListWidget.currentItem()
        if item is None:
            return None
        project = item.text()
        if project is not None and len(project) < 1:
            project = None
        return project

    def setCurrentProject(self, projectName):
        items = self.mainWindow.micProjectsListWidget.findItems(projectName,
                                                                Qt.MatchExactly)
        if len(items) > 0:
            self.mainWindow.micProjectsListWidget.setCurrentItem(items[0])

    def refresh(self):
        self.loadProjectList()
