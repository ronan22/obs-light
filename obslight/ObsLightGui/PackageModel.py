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
Created on 2 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QAbstractTableModel, QSize, Qt
from PySide.QtGui import QColor

from ObsLight.ObsLightPackageStatus import OBS_REV, OBS_STATUS, OSC_REV, OSC_STATUS, CHROOT_STATUS
from ObsLight.ObsLightPackageStatus import NameColumn, StatusColumn, FSStatusColumn, SyncStatusColumn


from ObsLight.ObsLightPackageStatus import ColumnHeaders, ColumnHeadersIndex
from ObsLight.ObsLightPackageStatus import StatusColorsDict
from ObsLight.ObsLightPackageStatus import StatusColumnCount

class PackageModel(QAbstractTableModel):
    '''
    QAbstractTableModel subclass to do the interface between the
    "packageTableWidget" and the ObsLightManager.
    '''
    __emptyList = {}
    colors = None

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        self.__pkgList = None
        self.__getPackageList()

        if self.colors is None:
            self.__loadColors()

    def __loadColors(self):
        self.colors = {}
        for columnLabel in StatusColorsDict.keys():
            self.colors[columnLabel] = {}
            for txt in StatusColorsDict[columnLabel].keys():
                color = StatusColorsDict[columnLabel][txt]
                self.colors[columnLabel][txt] = QColor(color)

    #model
    def rowCount(self, _parent=None):
        return len(self.__getPackageList())
    #model
    def columnCount(self, _parent=None):
        return StatusColumnCount()
    #model
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
    #model
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return ColumnHeaders[section]
        elif role == Qt.SizeHintRole:
            if orientation == Qt.Orientation.Vertical:
                pass
            else:
                if section == SyncStatusColumn:
                    return QSize(32, 0)
        return None

    def getProject(self):
        return self.__project

    def resetCache(self):
        self.__pkgList = None

    def __getPackageList(self):
        if self.getProject() is None:
            return self.__emptyList

        if self.__pkgList is None:
            self.__pkgList = self.__obsLightManager.getPackageInfo(self.getProject())

        if self.__pkgList is None:
            return self.__emptyList
        else:
            return self.__pkgList

    def displayRoleData(self, row, column):
        packageList = self.__getPackageList()
        packageName = sorted(packageList.keys())[row]
        columnIndex = ColumnHeadersIndex[column]
        return str(packageList[packageName].get(columnIndex, ""))

    def foregroundRoleData(self, index):
        row = index.row()
        column = index.column()
        drData = self.displayRoleData(row, column)

        color = self.colors[column].get(drData, None)
        return color

    def textAlignmentRoleData(self, index):
        column = index.column()
        if column in range(1, self.columnCount()):
            return Qt.AlignHCenter | Qt.AlignVCenter
        return None

#    def sort(self, Ncol, order):
#        print "Sort data according to column ", Ncol

    def refresh(self):
        self.resetCache()
        self.layoutChanged.emit()

    def addPackage(self, packageName):
        '''
        Add a package to the local project associated with this PackageModel.
        packageName must be an existing package name on the OBS server
        the project is associated to.
        '''
        self.__obsLightManager.addPackage(self.getProject(), packageName)
        self.refresh()

    def removePackage(self, packageName):
        '''
        Remove the package from the local project associated with this PackageModel.
        '''
        self.__obsLightManager.removePackage(self.getProject(), packageName)
        self.refresh()
