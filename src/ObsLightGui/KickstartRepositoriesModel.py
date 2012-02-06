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

from PySide.QtCore import QAbstractTableModel, Qt

class KickstartRepositoriesModel(QAbstractTableModel):

    NameColumn = 0
    UrlColumn = 1

    # A tuple containing the keys of repository dictionaries
    ColumnKeys = ("name", "baseurl")

    __manager = None
    __project = None
    __repositories = None
    __modified = False

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
        Load the repository list from Kickstart manager and sort it.
        """
        self.__repositories = self.manager.getKickstartRepositoryDictionaries(self.__project)
        self.__repositories.sort(key=lambda x: x["name"])
        self.layoutChanged.emit()

    # from QAbstractTableModel
    def columnCount(self, _parent=None):
        return 2

    # from QAbstractTableModel
    def rowCount(self, _parent=None):
        return len(self.__repositories)

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.NameColumn:
                    return "Name"
                elif section == self.UrlColumn:
                    return "URL"
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            # We double-clicking on cell (Qt.EditRole) we return
            # same data as on normal display
            return self.displayRoleData(index)
        return None

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            if value == self.displayRoleData(index):
                # nothing to do
                return False
            # in case repository name has changed, we must keep the old name
            oldName = self.__repositories[index.row()][self.ColumnKeys[self.NameColumn]]
            # do the change in memory
            self.__repositories[index.row()][self.ColumnKeys[index.column()]] = value
            # commit the change on disk
            self.__updateRepoInManager(index.row(), oldName)
            # update the view
            self.refresh()
            return True

    # from QAbstractTableModel
    def flags(self, index):
        """
        Calls `QAbstractTableModel.flags()` and add `Qt.ItemIsEditable` flag.
        In this model, all cells are editable.
        """
        return super(KickstartRepositoriesModel, self).flags(index) | Qt.ItemIsEditable

    def displayRoleData(self, index):
        """
        Return the "Qt.DisplayRole" data for cell at `index`.
        """
        return self.__repositories[index.row()][self.ColumnKeys[index.column()]]

    def __updateRepoInManager(self, row, oldName):
        """
        Remove the old repository,
        add the new one,
        flush the Kickstart file on disk.
        """
        repoDict = self.__repositories[row]
        self.manager.removeKickstartRepository(self.currentProject, oldName)
        self.manager.addKickstartRepository(self.currentProject, **repoDict)
        self.manager.saveKickstartFile(self.currentProject)
