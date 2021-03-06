# -*- coding: utf8 -*-
#
# Copyright 2011-2012, Intel Inc.
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

from PySide.QtCore import QAbstractTableModel, QSize, Qt
from PySide.QtGui import QColor

from ObsLight.ObsLightErr import ObsLightOscErr
STATUS_COLUMN = u"Status"


class PackageSourceFileManager(QAbstractTableModel):
    """
    A subclass of QAbstractTableModel which represents the file
    list of an osc working copy.
    """

    def __init__(self, obsLightManager, projectName, packageName):
        """
        Initialize the OscWorkingCopyModel.
        `obsLightManager`: a reference to the ObsLightManager.
        `projectName`: the name of the OBS project in which we are working.
        `packageName`: the name of the package we are managing the working copy of.
        """
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        self.__package = packageName
        self.__columnList = list()
        self.__fileList = list()
        self.__fileInfos = dict()
        self.sortKey = None
        self.sortOrder = Qt.SortOrder.AscendingOrder
        # dict<unicode, dict<object, QColor>>
        self.colors = dict()
        self._loadColors()
        self.refresh()

    def _loadColors(self):
        # http://www.w3.org/TR/SVG/types.html#ColorKeywords
        self.colors[STATUS_COLUMN] = {u' ': QColor(u"darkgreen"),
                                      u'A': QColor(u"green"),
                                      u'D': QColor(u"lightgray"),
                                      u'M': QColor(u"blue"),
                                      u'C': QColor(u"red"),
                                      u'?': QColor(u"black"),
                                      u'!': QColor(u"orange")}

    def clearColumns(self):
        """
        Clear the list of columns. Only keep one "File" column.
        """
        self.__columnList[:] = []
        self.__columnList.append(u"File")

    # from QAbstractTableModel
    def rowCount(self, _parent=None):
        return len(self.fileList())

    # from QAbstractTableModel
    def columnCount(self, _parent=None):
        return len(self.__columnList)

    # from QAbstractTableModel
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return self.__columnList[section]
        elif role == Qt.SizeHintRole:
            if orientation == Qt.Orientation.Vertical:
                pass
            else:
                if self.__columnList[section] == STATUS_COLUMN:
                    return QSize(48, 0)

    def displayRoleData(self, row, column):
        fileName = self.fileList()[row]
        if column == 0:
            return fileName
        elif column < self.columnCount():
            return self.__fileInfos[fileName].get(self.__columnList[column])
        return None

    def foregroundRoleData(self, index):
        row = index.row()
        column = index.column()
        if column == 0 and STATUS_COLUMN in self.__columnList:
            column = self.__columnList.index(STATUS_COLUMN)
        drData = self.displayRoleData(row, column)
        columnColors = self.colors.get(self.__columnList[column])
        if columnColors is not None:
            if column == self.__columnList.index(STATUS_COLUMN):
                return columnColors.get(drData[0])
            return columnColors.get(drData)
        return None

    def textAlignmentRoleData(self, index):
        column = index.column()
        if self.__columnList[column] == STATUS_COLUMN:
            return Qt.AlignHCenter | Qt.AlignVCenter
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index.row(), index.column())
        elif role == Qt.ForegroundRole:
            return self.foregroundRoleData(index)
        elif role == Qt.TextAlignmentRole:
            return self.textAlignmentRoleData(index)
        return None

    # from QAbstractTableModel
    def sort(self, Ncol, order):
        self.sortOrder = order
        if Ncol == 0:
            self.sortKey = None
        else:
            self.sortKey = lambda x: self.__fileInfos[x].get(self.__columnList[Ncol])
        self.refresh()

    def fileList(self):
        """
        Get the list of files of the working copy.
        """
        return self.__fileList

    def fileName(self, index):
        """
        Get the name of the file at `index`.
        """
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        return self.fileList()[index.row()]

    def refresh(self):
        """
        Refresh the list of files, and reload the list of columns.
        """
        files = self.__obsLightManager.getPackageParameter(self.__project,
                                                           self.__package,
                                                           "listFile")

        self.clearColumns()
        for fileName in files:
            # get informations about a file as a dictionary
            try:
                inf = self.__obsLightManager.getPackageFileInfo(self.__project,
                                                                self.__package,
                                                                fileName)
            #TODO: Match only "WorkingCopyInconsistent"
            except ObsLightOscErr as e:
                return e
            # search for new columns
            for key in inf.keys():
                if not key in self.__columnList:
                    self.__columnList.append(key)
            self.__fileInfos[fileName] = inf
        files.sort(reverse=(self.sortOrder == Qt.SortOrder.DescendingOrder),
                   key=self.sortKey)
        self.__fileList = files
        self.layoutChanged.emit()
