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
    """
    Class to manage the command list of the Kickstart file of a MIC project,
    except the "repo" command managed by `KickstartRepositoriesModel`.
    """

    NewCommandName = "NEW_COMMAND"
    NewCommandText = "# Enter command here\n"

    NameColumn = 0
    InUseColumn = 1
    GeneratedTextColumn = 2
    AliasesColumn = 3

    ColumnKeys = ("name", "in_use", "generated_text", "aliases")

    def __init__(self, obsLightManager, projectName):
        """
        `obsLightManager`: a reference to the ObsLightManager instance
        `projectName`: the name of the MIC project to manage Kickstart commands
        """
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartCommandDictionaries,
                                    sortOnKey=self.ColumnKeys[self.NameColumn])

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
        row = index.row()
        column = index.column()
        if row >= self.rowCount():
            return None
        if column == self.AliasesColumn:
            # aliases are maintained as a list of strings
            retVal = ", ".join(self.dataDict(row)[self.ColumnKeys[column]])
        else:
            retVal = self.dataDict(row)[self.ColumnKeys[column]]
        return retVal

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if index.column() == self.GeneratedTextColumn:
            if role == Qt.DisplayRole:
                self.__updateGeneratedText(index.row(), value)
                return True
        return False

    def __updateGeneratedText(self, row, value):
        """
        Update the "generated_text" attribute of command at `row` with `value`.
        Does not commit the change to ObsLightManager.
        """
        self.dataDict(row)[self.ColumnKeys[self.GeneratedTextColumn]] = value
        self.modified = True

    def commitChanges(self):
        """
        Commit all changes to ObsLightManager and write the Kickstart file.
        """
        for cmdDict in self.dataDictList():
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
        self.modified = False

    def refresh(self):
        """
        Reload the command list from Kickstart file (only if all
        modifications have been commited).
        """
        if not self.modified:
            super(KickstartCommandsModel, self).refresh()

    def newCommand(self):
        """
        Add a new empty command to the list. Command name
        will be `KickstartCommandsModel.NewCommandName` until
        changes are commited.
        """
        ck = KickstartCommandsModel.ColumnKeys
        newDict = {ck[KickstartCommandsModel.NameColumn]: KickstartCommandsModel.NewCommandName,
                   ck[KickstartCommandsModel.InUseColumn]: True,
                   ck[KickstartCommandsModel.GeneratedTextColumn]:
                                            KickstartCommandsModel.NewCommandText,
                   ck[KickstartCommandsModel.AliasesColumn]:
                                            [KickstartCommandsModel.NewCommandName]}
        self.dataDictList().append(newDict)
        self.modified = True

    def removeCommand(self, row):
        """
        Remove the command at `row`. It will not be removed from
        Kickstart file until changes are commited.
        """
        self.dataDict(row)[self.ColumnKeys[self.InUseColumn]] = False
        self.modified = True
