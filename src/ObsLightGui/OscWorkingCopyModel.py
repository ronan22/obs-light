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
Created on 13 déc. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QAbstractTableModel, Qt


class OscWorkingCopyModel(QAbstractTableModel):

    __obsLightManager = None
    __project = None
    __package = None
    __columnList = None
    __fileList = None
    __fileInfos = None

    sortKey = None
    sortOrder = Qt.SortOrder.AscendingOrder

    def __init__(self, obsLightManager, projectName, packageName):
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        self.__package = packageName
        self.__columnList = list()
        self.clearColumns()
        self.__fileList = list()
        self.__fileInfos = dict()
        self.refresh()

    def clearColumns(self):
        self.__columnList[:] = []
        self.__columnList.append(u"File")

    def rowCount(self, _parent=None):
        return len(self.fileList())

    def columnCount(self, _parent=None):
        return len(self.__columnList)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return self.__columnList[section]

    def displayRoleData(self, row, column):
        fileName = self.fileList()[row]
        if column == 0:
            return fileName
        elif column < self.columnCount():
            return self.__fileInfos[fileName].get(self.__columnList[column])
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index.row(), index.column())
        return None

    def sort(self, Ncol, order):
        self.sortOrder = order
        if Ncol == 0:
            self.sortKey = None
        else:
            self.sortKey = lambda x: self.__fileInfos[x].get(self.__columnList[Ncol])
        self.refresh()

    def fileList(self):
        return self.__fileList

    def refresh(self):
        files = self.__obsLightManager.getPackageParameter(self.__project,
                                                           self.__package,
                                                           u"listFile")
        for fileName in files:
            inf = self.__obsLightManager.getPackageFileInfo(self.__project,
                                                            self.__package,
                                                            fileName)
            for key in inf.keys():
                if not key in self.__columnList:
                    self.__columnList.append(key)
            self.__fileInfos[fileName] = inf
        files.sort(reverse=(self.sortOrder == Qt.SortOrder.DescendingOrder),
                   key=self.sortKey)
        self.__fileList = files
        self.layoutChanged.emit()
