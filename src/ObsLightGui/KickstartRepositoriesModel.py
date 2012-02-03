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
Created on 3 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import QAbstractTableModel, Qt

class KickstartRepositoriesModel(QAbstractTableModel):

    NameColumn = 0
    UrlColumn = 1

    __manager = None
    __project = None

    def __init__(self, obsLightManager, projectName):
        QAbstractTableModel.__init__(self)
        self.__manager = obsLightManager
        self.__project = projectName

    @property
    def manager(self):
        return self.__manager

    @property
    def currentProject(self):
        return self.__project

    def columnCount(self, _parent=None):
        return 2

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                if section == self.NameColumn:
                    return "Name"
                elif section == self.UrlColumn:
                    return "URL"
        return None

    def data(self, index, role=Qt.DisplayRole):
        # TODO: add method in manager to get repository list or repository dictionary list
        pass
