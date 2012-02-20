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
Created on 7 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import Qt
from KickstartModelBase import KickstartModelBase

class KickstartPackageGroupsModel(KickstartModelBase):
    """
    Class to manage the list of package groups of the Kickstart file of a MIC project.
    """

    NameColumn = 0
    ColumnKeys = ("name",)

    def __init__(self, obsLightManager, projectName):
        """
        `obsLightManager`: a reference to the ObsLightManager instance
        `projectName`: the name of the MIC project to manage Kickstart commands
        """
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartPackageGroupDictionaries,
                                    sortOnKey=self.ColumnKeys[self.NameColumn])

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.NameColumn:
                    return "Name"
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)
        return None

    def displayRoleData(self, index):
        """
        Return the `Qt.DisplayRole` data for cell at `index`.
        """
        retVal = self.dataDict(index.row())[self.ColumnKeys[index.column()]]
        return retVal if retVal is None else str(retVal)

    def addPackageGroup(self, name):
        """
        Add the package group `name` to the package section of the Kickstart file.
        """
        self.manager.addKickstartPackageGroup(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()

    def removePackageGroup(self, name):
        """
        Remove the package group `name` from the package section of the Kickstart file.
        """
        self.manager.removeKickstartPackageGroup(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()
