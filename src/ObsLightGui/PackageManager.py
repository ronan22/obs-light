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

from PySide.QtCore import QObject
from PySide.QtGui import QTableView

from PackageModel import PackageModel

class ObsPackageManager(QObject):
    '''
    
    '''

    __gui = None
    __obsLightManager = None
    __packageTableView = None
    __project = None
    __model = None

    def __init__(self, gui):
        '''
        
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__obsLightManager = gui.getObsLightManager()
        self.__packageTableView = gui.getMainWindow().findChild(QTableView,
                                                                  "packageTableView")
        
    def getCurrentProject(self):
        return self.__project
    
    def setCurrentProject(self, projectName):
        '''
        Set the current active project. It will refresh package list.
        Take care of not passing 0-length project name (None is valid).
        '''
        self.__project = projectName
        self.__model = PackageModel(self.__obsLightManager, projectName, self)
        self.__packageTableView.setModel(self.__model)
