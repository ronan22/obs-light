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
Created on 10 févr. 2012

@author: Florent Vennetier
'''

from os.path import basename

from PySide.QtCore import Qt
from KickstartModelBase import KickstartModelBase

class KickstartOverlayFilesModel(KickstartModelBase):

    SourceColumn = 0
    DestinationColumn = 1

    ColumnKeys = ("source", "destination")
    ColumnHeaders = ("Source", "Destination")

    def __init__(self, obsLightManager, projectName):
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartOverlayFileDictionaries,
                                    sortOnKey="source")

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return self.ColumnHeaders[section]
        return None

    # from QAbstractTableModel
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)
        elif role == Qt.EditRole:
            return self.editRoleData(index)
        return None

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            overlayDict = self.dataDict(row)
            src = overlayDict[self.ColumnKeys[self.SourceColumn]]
            dst = overlayDict[self.ColumnKeys[self.DestinationColumn]]
            self.manager.removeKickstartOverlayFile(self.currentProject, src, dst)
            if column == self.SourceColumn:
                src = value
            elif column == self.DestinationColumn:
                dst = value
            self.manager.addKickstartOverlayFile(self.currentProject, src, dst)
            self.manager.saveKickstartFile(self.currentProject)
            self.refresh()
            return True
        return False

    # from QAbstractTableModel
    def flags(self, index):
        """
        Calls `QAbstractTableModel.flags()` and add `Qt.ItemIsEditable` flag.
        In this model, all cells except column SslVerifyColumn are editable.
        Cells of column SslVerifyColumn are checkable.
        """
        superFlags = super(KickstartOverlayFilesModel, self).flags(index)
        superFlags = superFlags | Qt.ItemFlag.ItemIsEditable
        return superFlags

    def displayRoleData(self, index):
        """
        Return the `Qt.DisplayRole` data for cell at `index`.
        """
        if index.row() >= self.rowCount():
            return None
        retVal = self.editRoleData(index)
        if index.column() == self.SourceColumn:
            retVal = basename(retVal)
        return retVal

    def editRoleData(self, index):
        """
        Return the `Qt.EditRole` data for cell at `index`.
        """
        row = index.row()
        if row >= self.rowCount():
            return None
        return self.dataDict(row).get(self.ColumnKeys[index.column()], None)

    def newOverlayFile(self, source="/dev/null", destination="/tmp/"):
        """
        Add a new overlay file with `source` and `destination`.
        The Kickstart file is automatically saved.
        """
        self.manager.addKickstartOverlayFile(self.currentProject, source, destination)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()

    def removeOverlayFiles(self, rows):
        """
        Remove the overlay files at `rows`.
        The Kickstart file is automatically saved.
        """
        for row in rows:
            overlayDict = self.dataDict(row)
            src = overlayDict[self.ColumnKeys[self.SourceColumn]]
            dst = overlayDict[self.ColumnKeys[self.DestinationColumn]]
            self.manager.removeKickstartOverlayFile(self.currentProject, src, dst)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()
