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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
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
    OscStatusColumn = 1
    OscRevColumn = 2
    ObsStatusColumn = 3
    ObsRevColumn = 4
    ChrootStatusColumn = 5

    StatusOnServerColors = {}
    StatusInChRootColors = {}
    StatusInOscColors = {}

    __obsLightManager = None
    __project = None
    __emptyList = []

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        # http://www.w3.org/TR/SVG/types.html#ColorKeywords
        self.StatusOnServerColors["succeeded"] = QColor("green")
        self.StatusOnServerColors["excluded"] = QColor("grey")
        self.StatusOnServerColors["broken"] = QColor("red")
        self.StatusOnServerColors["building"] = QColor("gold")
        self.StatusOnServerColors["failed"] = QColor("red")
        self.StatusOnServerColors["scheduled"] = QColor("blue")
        self.StatusOnServerColors["unresolvable"] = QColor("darkred")
        self.StatusInChRootColors["Installed"] = QColor("green")
        self.StatusInOscColors["Unknown"] = QColor("grey")
        self.StatusInOscColors["Succeeded"] = QColor("green")
        self.StatusInOscColors["inconsistent state"] = QColor("red")

    def getProject(self):
        return self.__project

    def __getPackageList(self):
        if self.getProject() is None:
            return self.__emptyList
        pkgList = self.__obsLightManager.getLocalProjectPackageList(self.getProject(),
                                                                    local=1)
        if pkgList is None:
            return self.__emptyList
        else:
            return pkgList

    def rowCount(self, _parent=None):
        return len(self.__getPackageList())

    def columnCount(self, _parent=None):
        return 6

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
                    return u"Chroot status"
                elif section == self.OscStatusColumn:
                    return u"OSC status"
                elif section == self.OscRevColumn:
                    return u"Rev"
                elif section == self.ObsRevColumn:
                    return u"Rev"
        elif role == Qt.SizeHintRole:
            if orientation == Qt.Orientation.Vertical:
                pass
            else:
                if section == self.OscRevColumn:
                    return QSize(32, 0)
                elif section == self.ObsRevColumn:
                    return QSize(32, 0)
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return None
        if role == Qt.DisplayRole or role == Qt.ForegroundRole:
            packageName = self.__getPackageList()[index.row()]
            if index.column() == self.NameColumn and role == Qt.DisplayRole:
                return packageName
            elif index.column() == self.ObsStatusColumn:
                status = self.__obsLightManager.getPackageStatus(self.__project,
                                                                 packageName)
                if role == Qt.DisplayRole:
                    return status
                elif role == Qt.ForegroundRole:
                    return self.StatusOnServerColors.get(status, None)
            elif index.column() == self.ChrootStatusColumn:
                status = self.__obsLightManager.getGetChRootStatus(self.__project,
                                                                   packageName)
                if role == Qt.DisplayRole:
                    return status
                elif role == Qt.ForegroundRole:
                    return self.StatusInChRootColors.get(status, None)
            elif index.column() == self.OscStatusColumn:
                status = self.__obsLightManager.getOscPackageStatus(self.__project,
                                                                    packageName)
                if role == Qt.DisplayRole:
                    return status
                elif role == Qt.ForegroundRole:
                    return self.StatusInOscColors.get(status, None)
            elif index.column() == self.OscRevColumn:
                rev = self.__obsLightManager.getOscPackageRev(self.__project,
                                                              packageName)
                if role == Qt.DisplayRole:
                    return rev
            elif index.column() == self.ObsRevColumn:
                rev = self.__obsLightManager.getObsPackageRev(self.__project,
                                                              packageName)
                if role == Qt.DisplayRole:
                    return rev
        return None

    def sort(self, Ncol, order):
        print "Sort data according to column ", Ncol

    def refresh(self):
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
