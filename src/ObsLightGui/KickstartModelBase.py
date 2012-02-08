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
Created on 7 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QAbstractTableModel

class KickstartModelBase(QAbstractTableModel):
    """
    Base class for KickstartPackagesModel and KickstartRepositoriesModel
    """

    __manager = None
    __project = None
    __dataDictList = None

    __getDataDictListFunc = None

    # The index if the name column
    NameColumn = 0
    # The keys to get values for the different columns from __dataDictList dictionaries
    ColumnKeys = ("name",)

    def __init__(self, obsLightManager, projectName, getDataDictListFunc):
        """
        Initialize the model.
          obsLightManager:  an instance of `ObsLightManager`
          projectName:  the name of the MIC project this model will retrieve data from
          getDataDictListFunc:  a function taking a project name as parameter and
              returning a list of data dictionaries
        """
        QAbstractTableModel.__init__(self)
        self.__manager = obsLightManager
        self.__project = projectName
        self.__getDataDictListFunc = getDataDictListFunc
        self.refresh()

    @property
    def manager(self):
        return self.__manager

    @property
    def currentProject(self):
        return self.__project

    # from QAbstractTableModel
    def columnCount(self, _parent=None):
        return len(self.ColumnKeys)

    # from QAbstractTableModel
    def rowCount(self, _parent=None):
        return len(self.__dataDictList)

    def dataDict(self, row):
        """
        Get the dictionary holding data for `row`.
        """
        return self.__dataDictList[row]

    def dataDictList(self):
        return self.__dataDictList

    def refresh(self):
        """
        Load the data dictionary list from Kickstart manager,
        sort it according to the "name" values,
        and emit `QAbstractItemModel.layoutChanged`.
        """
        self.__dataDictList = self.__getDataDictListFunc(self.__project)
        self.__dataDictList.sort(key=lambda x: x["name"])
        self.layoutChanged.emit()
