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
Created on 6 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import Qt
from KickstartModelBase import KickstartModelBase

class KickstartPackagesModel(KickstartModelBase):
    """
    Class to manage the list of packages of the Kickstart file of a MIC project.
    """

    NameColumn = 0
    ExcludedColumn = 1

    ColumnKeys = ("name", "excluded")

    def __init__(self, obsLightManager, projectName):
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartPackageDictionaries,
                                    self.ColumnKeys[self.NameColumn])

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.NameColumn:
                    return "Name"
                elif section == self.ExcludedColumn:
                    return "Included"
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)
        elif role == Qt.CheckStateRole:
            return self.checkStateRoleData(index)
        elif role == Qt.TextAlignmentRole:
            return self.textAlignmentRoleData(index)
        return None

    def displayRoleData(self, index):
        """
        Return the `Qt.DisplayRole` data for cell at `index`.
        """
        if index.column() == self.ExcludedColumn:
            return None
        retVal = self.dataDict(index.row())[self.ColumnKeys[index.column()]]
        return retVal if retVal is None else str(retVal)

    def checkStateRoleData(self, index):
        """
        Return the `Qt.CheckStateRole` data for cell at `index`.
        Returning None for all columns, except ExcludedColumn:
          Qt.CheckState.Checked if package is explicitly excluded,
          Qt.CheckState.Unchecked otherwise
        """
        if index.column() == self.ExcludedColumn:
            included = not self.dataDict(index.row())[self.ColumnKeys[self.ExcludedColumn]]
            return Qt.CheckState.Checked if included else Qt.CheckState.Unchecked
        return None

    # from QAbstractTableModel
    def flags(self, index):
        """
        Returns `Qt.ItemIsEnabled | Qt.ItemIsUserCheckable` for items in ExcludedColumn,
         `Qt.ItemIsEnabled` for other columns
        """
        if index.column() == self.ExcludedColumn:
            superFlags = Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable
        else:
            superFlags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return superFlags

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            if index.column() == self.ExcludedColumn:
                excluded = (value != Qt.CheckState.Checked)
                self.dataDict(index.row())[self.ColumnKeys[self.ExcludedColumn]] = excluded
                self.__updatePackageInKs(index.row())
                return True
        return False

    def __updatePackageInKs(self, row):
        """
        Update the Kickstart file with the last status of the package at `row`.
        """
        pkgDict = self.dataDict(row)
        self.manager.removeKickstartPackage(self.currentProject,
                                            pkgDict[self.ColumnKeys[self.NameColumn]])
        self.manager.addKickstartPackage(self.currentProject,
                                         pkgDict[self.ColumnKeys[self.NameColumn]],
                                         pkgDict[self.ColumnKeys[self.ExcludedColumn]])
        self.manager.saveKickstartFile(self.currentProject)

    def addPackage(self, name):
        """
        Add the package `name` in the package section of the Kickstart file.
        """
        self.manager.addKickstartPackage(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()

    def removePackage(self, name):
        """
        Remove the package `name` from the package section
        of the Kickstart file.
        """
        self.manager.removeKickstartPackage(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()
