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

from PySide.QtCore import QAbstractTableModel, Qt

class KickstartModelBase(QAbstractTableModel):
    """
    Subclass of QAbstractTableModel, base class for Kickstart management
    classes. Auto-loads entries when `refresh` is called.
    Implements `columnCount` and `rowCount` required by QAbstractTableModel.
    """
    # pylint: disable-msg=E0202, E1101

    # The index of the name column
    NameColumn = 0
    # The keys to get values for the different columns from __dataDictList dictionaries
    ColumnKeys = ("name",)

    def __init__(self, obsLightManager, projectName, getDataDictListFunc, sortOnKey=None):
        """
        Initialize the model.
          obsLightManager:  an instance of `ObsLightManager`
          projectName:  the name of the MIC project this model will retrieve data from
          getDataDictListFunc:  a function taking a project name as parameter and
              returning a list of data dictionaries
        """
        QAbstractTableModel.__init__(self)
        self.__modified = False
        self.__dataDictList = None
        self.__manager = obsLightManager
        self.__project = projectName
        self.__getDataDictListFunc = getDataDictListFunc
        self.sortOnKey = sortOnKey
        self.refresh()

    @property
    def manager(self):
        return self.__manager

    @property
    def currentProject(self):
        return self.__project

    @property
    def modified(self):
        """
        Return True if some modifications have not been commited,
        False otherwise.
        """
        return self.__modified

    @modified.setter
    def modified(self, value): # pylint: disable-msg=E0102
        self.__modified = value
        self.layoutChanged.emit()

    # from QAbstractTableModel
    def columnCount(self, _parent=None):
        # Must stay self.ColumnKeys, and not KickstartModelBase.columnKey,
        # otherwise subclasses won't get their own column count
        # but the one of this base class
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
        """
        Get the internal list of data dictionaries.
        """
        return self.__dataDictList

    def textAlignmentRoleData(self, index):
        if (self.flags(index) & Qt.ItemFlag.ItemIsUserCheckable) > 0:
            return Qt.AlignHCenter | Qt.AlignVCenter
        return None

    def refresh(self):
        """
        Load the data dictionary list from Kickstart manager,
        sort it according to the "name" values,
        and emit `QAbstractItemModel.layoutChanged`.
        """
        self.__dataDictList = self.__getDataDictListFunc(self.__project)
        if self.sortOnKey is not None:
            self.__dataDictList.sort(key=lambda x: x[self.sortOnKey])
        self.layoutChanged.emit()
