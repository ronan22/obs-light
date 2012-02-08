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
Created on 8 févr. 2012

@author: Florent Vennetier
'''
from PySide.QtCore import Qt

from KickstartModelBase import KickstartModelBase

class KickstartCommandsModel(KickstartModelBase):

    NewCommandName = "NEW_COMMAND"

    NameColumn = 0
    InUseColumn = 1
    GeneratedTextColumn = 2

    ColumnKeys = ("name", "in_use", "generated_text")

    __modified = False

    def __init__(self, obsLightManager, projectName):
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartCommandDictionaries)

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)

    def displayRoleData(self, index):
        """
        Return the `Qt.DisplayRole` data for cell at `index`.
        """
        retVal = self.dataDict(index.row())[self.ColumnKeys[index.column()]]
        return retVal

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if index.column() == self.GeneratedTextColumn:
            if role == Qt.DisplayRole:
                self.__updateGeneratedText(index.row(), value)
                return True
        return False

    def __updateGeneratedText(self, row, value):
        self.dataDict(row)[self.ColumnKeys[self.GeneratedTextColumn]] = value
        self.__modified = True

    def commitChanges(self):
        for cmdDict in [self.dataDict(row) for row in range(self.rowCount())]:
            cmd = cmdDict[self.ColumnKeys[self.NameColumn]]
            if cmd == self.NewCommandName:
                cmd = None
            inUse = cmdDict[self.ColumnKeys[self.InUseColumn]]
            if inUse:
                cmdText = cmdDict[self.ColumnKeys[self.GeneratedTextColumn]]
                self.manager.addOrChangeKickstartCommand(self.currentProject, cmdText, cmd)
            else:
                self.manager.removeKickstartCommand(self.currentProject, cmd)
        self.manager.saveKickstartFile(self.currentProject)
        self.__modified = False

    def refresh(self):
        if not self.__modified:
            super(KickstartCommandsModel, self).refresh()

    def hasBeenModified(self):
        return self.__modified

    def getUnusedCommandList(self):
        unusedCommands = []
        # maybe we should create a method returning the original list...
        for cmdDict in [self.dataDict(row) for row in range(self.rowCount())]:
            if not cmdDict[self.ColumnKeys[self.InUseColumn]]:
                unusedCommands.append(cmdDict[self.ColumnKeys[self.NameColumn]])
        return unusedCommands

    def activateCommand(self, command):
        for cmdDict in [self.dataDict(row) for row in range(self.rowCount())]:
            if cmdDict[self.ColumnKeys[self.NameColumn]] == command:
                cmdDict[self.ColumnKeys[self.InUseColumn]] = True
                break

    def newCommand(self):
        newDict = {self.ColumnKeys[self.NameColumn]: self.NewCommandName,
                   self.ColumnKeys[self.InUseColumn]: True,
                   self.ColumnKeys[self.GeneratedTextColumn]: "# Enter command here\n"}
        self.dataDictList().insert(0, newDict)

    def removeCommand(self, row):
        self.dataDict(row)[self.ColumnKeys[self.InUseColumn]] = False
