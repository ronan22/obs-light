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

from PySide.QtCore import QAbstractTableModel, Qt

class PackageModel(QAbstractTableModel):
    '''
    QAbstractTableModel subclass to do the interface between the
    "packageTableWidget" and the ObsLightManager.
    '''
    
    PackageNameColumn = 0
    PackageStatusColumn = 1
    
    __obsLightManager = None
    __project = None
    __emptyList = []

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__obsLightManager = obsLightManager
        self.__project = projectName
        
    def getProject(self):
        return self.__project
        
    def __getPackageList(self):
        if self.getProject() is None:
            return self.__emptyList
        return self.__obsLightManager.getLocalProjectPackageList(self.getProject(), local=1)
    
    def rowCount(self, _parent=None):
        return len(self.__getPackageList())
    
    def columnCount(self, _parent=None):
        return 2

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.PackageNameColumn:
                    return "Package"
                elif section == self.PackageStatusColumn:
                    return "Status"
                else:
                    return None
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            packageName = self.__getPackageList()[index.row()]
            if index.column() == self.PackageNameColumn:
                return packageName
            elif index.column() == self.PackageStatusColumn:
                # TODO: rewrite with simplified getPackageStatus method when it's available
                obsServer = self.__obsLightManager.getProjectParameter(self.__project, "obsServer")
                projectObsName = self.__obsLightManager.getProjectParameter(self.__project,
                                                                            "projectObsName")
                arch = self.__obsLightManager.getProjectParameter(self.__project,
                                                                   "projectArchitecture")
                target = self.__obsLightManager.getProjectParameter(self.__project,
                                                                    "projectTarget")
                return self.__obsLightManager.getPackageStatus(obsServer, projectObsName,
                                                               packageName, target, arch)
        else:
            return None

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
