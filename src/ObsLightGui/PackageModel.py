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
Created on 2 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QAbstractTableModel, QSize, Qt
from PySide.QtGui import QColor

class PackageModel(QAbstractTableModel):
    '''
    QAbstractTableModel subclass to do the interface between the
    "packageTableWidget" and the ObsLightManager.
    '''

    NameColumn = 0
    OscStatusColumn = 3
    OscRevColumn = 4
    ObsStatusColumn = 1
    ObsRevColumn = 2
    ChrootStatusColumn = 5

    colors = list(({}, {}, {}, {}, {}, {}))

    __obsLightManager = None
    __project = None
    __emptyList = {}
    __pkgList = None

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        self.__getPackageList()
        self._loadColors()

    #model
    def rowCount(self, _parent=None):
        return len(self.__getPackageList())
    #model
    def columnCount(self, _parent=None):
        return 6
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
                if section == self.NameColumn:
                    return u"Package"
                elif section == self.ObsStatusColumn:
                    return u"OBS status"
                elif section == self.ChrootStatusColumn:
                    return u"Filesystem status"
                elif section == self.OscStatusColumn:
                    return u"Local status"
                elif section == self.OscRevColumn:
                    return u"Rev"
                elif section == self.ObsRevColumn:
                    return u"Rev"
        elif role == Qt.SizeHintRole:
            if orientation == Qt.Orientation.Vertical:
                pass
            else:
                if section == self.OscRevColumn or section == self.ObsRevColumn:
                    return QSize(32, 0)
        return None

    def _loadColors(self):
        # http://www.w3.org/TR/SVG/types.html#ColorKeywords
        self.colors[self.ObsStatusColumn]["succeeded"] = QColor(u"green")
        self.colors[self.ObsStatusColumn]["excluded"] = QColor(u"grey")
        self.colors[self.ObsStatusColumn]["broken"] = QColor(u"red")
        self.colors[self.ObsStatusColumn]["building"] = QColor(u"gold")
        self.colors[self.ObsStatusColumn]["failed"] = QColor(u"red")
        self.colors[self.ObsStatusColumn]["scheduled"] = QColor(u"blue")
        self.colors[self.ObsStatusColumn]["unresolvable"] = QColor(u"darkred")

        self.colors[self.ChrootStatusColumn]["Installed"] = QColor(u"green")

        self.colors[self.OscStatusColumn]["Unknown"] = QColor(u"grey")
        self.colors[self.OscStatusColumn]["Succeeded"] = QColor(u"green")
        self.colors[self.OscStatusColumn]["inconsistent state"] = QColor(u"red")
        # "inferior" means oscRev < obsRev
        self.colors[self.OscRevColumn][u"inferior"] = QColor(u"red")
        self.colors[self.OscRevColumn][u"equal"] = QColor(u"green")
        # "superior" means oscRev > obsRev, which should never happen
        self.colors[self.OscRevColumn][u"superior"] = QColor(u"red")
        self.colors[self.ObsRevColumn][u"ok"] = QColor(u"green")

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
        retVal = None

        if column == self.NameColumn:
            retVal = packageName
        elif column == self.ObsStatusColumn:
            retVal = packageList[packageName]["status"]
        elif column == self.ChrootStatusColumn:
            retVal = packageList[packageName]["chRootStatus"]
        elif column == self.OscStatusColumn:
            retVal = packageList[packageName]["oscStatus"]
        elif column == self.OscRevColumn:
            retVal = packageList[packageName]["oscRev"]
        elif column == self.ObsRevColumn:
            retVal = packageList[packageName]["obsRev"]
        return retVal

    def foregroundRoleData(self, index):
        row = index.row()
        column = index.column()
        drData = self.displayRoleData(row, column)
        if column == self.OscRevColumn:
            obsRev = self.displayRoleData(row, self.ObsRevColumn)
            if drData < obsRev:
                drData = u"inferior"
            elif drData == obsRev:
                drData = u"equal"
            else:
                drData = u"superior"
        if column == self.ObsRevColumn:
            drData = u"ok"
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
