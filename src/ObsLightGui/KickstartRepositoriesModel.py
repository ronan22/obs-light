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

from PySide.QtCore import Qt
from KickstartModelBase import KickstartModelBase

class KickstartRepositoriesModel(KickstartModelBase):

    NameColumn = 0
    UrlColumn = 1
    PriorityColumn = 2
    SslVerifyColumn = 3

    # A tuple containing the keys of repository dictionaries
    ColumnKeys = ("name", "baseurl", "priority", "ssl_verify")

    def __init__(self, obsLightManager, projectName):
        self.__modified = False
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartRepositoryDictionaries,
                                    self.ColumnKeys[self.NameColumn])

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
                elif section == self.PriorityColumn:
                    return "Priority"
                elif section == self.SslVerifyColumn:
                    return "SSL verification"
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            # We double-clicking on cell (Qt.EditRole) we return
            # same data as on normal display
            return self.displayRoleData(index)
        elif role == Qt.CheckStateRole:
            return self.checkStateRoleData(index)
        return None

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            if value == self.displayRoleData(index):
                # nothing to do
                return False
            # convert empty strings and "none" to None
            if column == self.PriorityColumn:
                if isinstance(value, basestring) and (value.lower() == "none" or value == ""):
                    value = None
            # in case repository name has changed, we must keep the old name
            oldName = self.dataDict(row)[self.ColumnKeys[self.NameColumn]]
            # do the change in memory
            self.dataDict(row)[self.ColumnKeys[column]] = value
            # commit the change on disk
            self.__updateRepoInManager(row, oldName)
            # update the view
            self.refresh()
            return True
        elif role == Qt.CheckStateRole:
            if column == self.SslVerifyColumn:
                if value == Qt.CheckState.Checked:
                    self.dataDict(row)[self.ColumnKeys[column]] = "yes"
                else:
                    self.dataDict(row)[self.ColumnKeys[column]] = "no"
        return False

    # from QAbstractTableModel
    def flags(self, index):
        """
        Calls `QAbstractTableModel.flags()` and add `Qt.ItemIsEditable` flag.
        In this model, all cells except column SslVerifyColumn are editable.
        Cells of column SslVerifyColumn are checkable.
        """
        superFlags = super(KickstartRepositoriesModel, self).flags(index)
        if index.column() == self.SslVerifyColumn:
            superFlags = superFlags | Qt.ItemIsUserCheckable
        else:
            superFlags = superFlags | Qt.ItemIsEditable
        return superFlags

    def displayRoleData(self, index):
        """
        Return the "Qt.DisplayRole" data for cell at `index`.
        """
        if index.column() == self.SslVerifyColumn:
            return None
        retVal = self.dataDict(index.row())[self.ColumnKeys[index.column()]]
        return retVal if retVal is None else str(retVal)

    def checkStateRoleData(self, index):
        """
        Return the `Qt.CheckStateRole` data for cell at `index`.
        Returning None for all columns, except SslVerifyColumn:
          Qt.CheckState.Checked if SSL verification is "yes",
          Qt.CheckState.Unchecked otherwise
        """
        if index.column() == self.SslVerifyColumn:
            verify = self.dataDict(index.row())[self.ColumnKeys[self.SslVerifyColumn]]
            return Qt.CheckState.Checked if verify.lower() == "yes" else Qt.CheckState.Unchecked
        return None

    def __updateRepoInManager(self, row, oldName):
        """
        Remove the old repository,
        add the new one,
        flush the Kickstart file on disk.
        """
        repoDict = self.dataDict(row)
        self.manager.removeKickstartRepository(self.currentProject, oldName)
        # pylint: disable-msg=W0142
        self.manager.addKickstartRepository(self.currentProject, **repoDict)
        self.manager.saveKickstartFile(self.currentProject)

    def addRepository(self, name, url):
        sslVerify = "yes" if url.startswith("https") else "no"
        self.manager.addKickstartRepository(self.currentProject, baseurl=url,
                                            name=name,
                                            ssl_verify=sslVerify)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()

    def removeRepository(self, name):
        self.manager.removeKickstartRepository(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()
