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
from KickstartModelBase import KickstartModelBase

class KickstartRepositoriesModel(KickstartModelBase):

    NameColumn = 0
    UrlColumn = 1
    CostColumn = 2
    PriorityColumn = 3
    SslVerifyColumn = 4

    # A tuple containing the keys of repository dictionaries
    ColumnKeys = ("name", "baseurl", "cost", "priority", "ssl_verify")

    __modified = False

    def __init__(self, obsLightManager, projectName):
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartRepositoryDictionaries)

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
                elif section == self.CostColumn:
                    return "Cost (for Yum)"
                elif section == self.PriorityColumn:
                    return "Priority (for Zypper)"
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
        return None

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            if value == self.displayRoleData(index):
                # nothing to do
                return False
            row = index.row()
            column = index.column()
            # convert empty strings and "none" to None
            if column in (self.CostColumn, self.PriorityColumn):
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
        retVal = self.dataDict(index.row())[self.ColumnKeys[index.column()]]
        return retVal if retVal is None else str(retVal)

    def __updateRepoInManager(self, row, oldName):
        """
        Remove the old repository,
        add the new one,
        flush the Kickstart file on disk.
        """
        repoDict = self.dataDict(row)
        self.manager.removeKickstartRepository(self.currentProject, oldName)
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
