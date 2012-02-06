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


from PySide.QtCore import QAbstractTableModel, Qt

class KickstartPackagesModel(QAbstractTableModel):

    NameColumn = 0
    ExcludedColumn = 1

    ColumnKeys = ("name", "excluded")

    __manager = None
    __project = None
    __packages = None

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__manager = obsLightManager
        self.__project = projectName
        self.refresh()

    @property
    def manager(self):
        return self.__manager

    @property
    def currentProject(self):
        return self.__project

    def refresh(self):
        """
        Load the package list from Kickstart manager and sort it.
        """
        self.__packages = self.manager.getKickstartPackageDictionaries(self.currentProject)
        self.__packages.sort(key=lambda x: x["name"])
        self.layoutChanged.emit()

    # from QAbstractTableModel
    def columnCount(self, _parent=None):
        return 2

    # from QAbstractTableModel
    def rowCount(self, _parent=None):
        return len(self.__packages)

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.NameColumn:
                    return "Name"
                elif section == self.ExcludedColumn:
                    return "Excluded"
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)
        elif role == Qt.CheckStateRole:
            return self.checkStateRoleData(index)
        return None

    def displayRoleData(self, index):
        """
        Return the "Qt.DisplayRole" data for cell at `index`.
        """
        retVal = self.__packages[index.row()][self.ColumnKeys[index.column()]]
        return retVal if retVal is None else str(retVal)

    def checkStateRoleData(self, index):
        if index.column() == self.ExcludedColumn:
            excluded = self.__packages[index.row()][self.ColumnKeys[self.ExcludedColumn]]
            return Qt.CheckState.Checked if excluded else Qt.CheckState.Unchecked
        return None

    # from QAbstractTableModel
    def flags(self, index):
        """
        Calls `QAbstractTableModel.flags()` and add `Qt.ItemIsEditable` flag.
        In this model, all cells are editable.
        """
        superFlags = super(KickstartPackagesModel, self).flags(index)
        if index.column == self.ExcludedColumn:
            superFlags = superFlags | Qt.ItemIsUserCheckable
        return superFlags
