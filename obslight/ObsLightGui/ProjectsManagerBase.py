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
Created on 3 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, Qt

class ProjectsManagerBase(QObject):
    """
    Base class for MicProjectsManager and ObsProjectsManager.
    Handles the loading of a list of projects, and provide a method
    to get the currently selected project in the UI.
    """
    # pylint: disable-msg=E0202, E1101

    def __init__(self, projectListWidget, projectListFunc):
        """
        Initialize a ProjectsManagerBase with:
          projectListWidget: a QListWidget instance where the projects will be loaded
          projectListFunc: a function returning a list of project names
        """
        QObject.__init__(self)
        self.__projectListFunc = projectListFunc
        self.__projectListWidget = projectListWidget

    @property
    def projectListWidget(self):
        """
        The `QtGui.QListWidget` object containing the project list.
        """
        return self.__projectListWidget

    @property
    def currentProject(self):
        """
        The name of the project selected in the UI, or None.
        """
        item = self.projectListWidget.currentItem()
        if item is None:
            return None
        project = item.text()
        if project is not None and len(project) < 1:
            project = None
        return project

    @currentProject.setter
    def currentProject(self, value): # pylint: disable-msg=E0102
        """
        The name of the project selected in the UI, or None.
        """
        items = self.projectListWidget.findItems(value,
                                                 Qt.MatchExactly)
        if len(items) > 0:
            self.projectListWidget.setCurrentItem(items[0])

    def loadProjectList(self):
        """
        Load (or reload) the project list.
        """
        lastCurrentProject = self.currentProject
        projectList = self.__projectListFunc()
        self.projectListWidget.clear()
        self.projectListWidget.addItems(projectList)
        if lastCurrentProject is not None and lastCurrentProject in projectList:
            self.currentProject = lastCurrentProject

    def refresh(self):
        """
        Reload the project list.
        Tries to keep the current project selected.
        """
        self.loadProjectList()
