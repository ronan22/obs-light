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
Created on 28 sept. 2011

@author: Florent Vennetier
'''

# TODO: replace internal calls to __projectList by an OBSLightManager mock

from PySide.QtCore import QAbstractListModel, Qt

class ObsProjectListModel(QAbstractListModel):
    '''
    classdocs
    '''
    dataRole = Qt.UserRole + 1
    __obsLightManager = None
    __projectList = []  # TODO: use a dictionary instead of a list

    def __init__(self, obsLightManager=None):
        '''
        Constructor
        '''
        QAbstractListModel.__init__(self)
        self.__obsLightManager = obsLightManager
        
    def __getProjectList(self):
        return self.__obsLightManager.getLocalProjectList()
        
    def data(self, index, role):
        if role == 0:
            return str(self.__getProjectList()[index.row()])
        elif role == self.dataRole:
            return self.__getProjectList()[index.row()]
        else:
            return None
        
    def rowCount(self, parent=None):
        return len(self.__getProjectList())
        
    def addProject(self, name, server, target, architecture):
        self.__obsLightManager.addProject(name, target=target, architecture=architecture)
        rowCount = self.rowCount()
        self.dataChanged.emit(self.createIndex(rowCount - 1, 0), self.createIndex(rowCount, 0))
        
    def modifyProject(self, name, server, target, architecture):
        self.__obsLightManager.modifyProject(name, target=target, architecture=architecture)
    
    def deleteProject(self, name):
        self.__obsLightManager.deleteProject(name)
        rowCount = self.rowCount()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(rowCount, 0))
