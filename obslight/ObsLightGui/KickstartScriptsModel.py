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
Created on 9 févr. 2012

@author: Florent Vennetier
'''

from PySide.QtCore import Qt

from KickstartModelBase import KickstartModelBase

class KickstartScriptsModel(KickstartModelBase):
    """
    Class to manage the scripts of the Kickstart file of a MIC project.
    """

    NewScriptName = "NEW_UNSAVED_SCRIPT"
    NewScriptText = "# Enter script here\n"
    NewScriptInterpreter = "/bin/sh"
    NewScriptType = 0

    NameColumn = 0
    ScriptColumn = 1
    TypeColumn = 2
    InterpreterColumn = 3
    ErrorOnFailColumn = 4
    RunInChrootColumn = 5
    LogFileColumn = 6

    ColumnKeys = ("name", "script", "type", "interp", "errorOnFail",
                  "inChroot", "logfile")
    ColumnHeaders = ("Name", "Script", "Type", "Interpreter", "Error on fail",
                     "Run in chroot", "Log file")

    def __init__(self, obsLightManager, projectName):
        """
        `obsLightManager`: a reference to the ObsLightManager instance
        `projectName`: the name of the MIC project to manage Kickstart commands
        """
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartScriptDictionaries)
        self._scriptsToRemove = []

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return self.ColumnHeaders[section]
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.displayRoleData(index)
        return None

    def displayRoleData(self, index):
        """
        Return the `Qt.DisplayRole` data for cell at `index`.
        """
        row = index.row()
        if row >= self.rowCount():
            return None
        retVal = self.dataDict(row).get(self.ColumnKeys[index.column()], None)
        return retVal

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.DisplayRole:
            self.dataDict(index.row())[self.ColumnKeys[index.column()]] = value
            self.modified = True
            return True
        return False

    def commitChanges(self):
        """
        Commit all changes to the scripts and write the Kickstart file.
        """
        while len(self._scriptsToRemove) > 0:
            scriptDict = self._scriptsToRemove[0]
            self.manager.removeKickstartScript(self.currentProject,
                                               scriptDict[self.ColumnKeys[self.NameColumn]])
            del self._scriptsToRemove[0]
        for scriptDict in self.dataDictList():
            if scriptDict[self.ColumnKeys[self.NameColumn]] == self.NewScriptName:
                exportDict = dict(scriptDict)
                exportDict[self.ColumnKeys[self.NameColumn]] = None
            else:
                exportDict = scriptDict
            # pylint: disable-msg=W0142
            self.manager.addOrChangeKickstartScript(self.currentProject,
                                                    **exportDict)
        self.manager.saveKickstartFile(self.currentProject)
        self.modified = False

    def refresh(self):
        """
        Reload the script list from Kickstart file (only if all
        modifications have been commited).
        """
        if not self.modified:
            super(KickstartScriptsModel, self).refresh()

    def newScript(self):
        """
        Add a new script. Will not be added to the Kickstart file
        until `commitChanges()` is called.
        """
        ck = self.ColumnKeys
        scriptDict = {ck[self.NameColumn]: self.NewScriptName,
                      ck[self.ScriptColumn]: self.NewScriptText,
                      ck[self.TypeColumn]: self.NewScriptType,
                      ck[self.InterpreterColumn]: self.NewScriptInterpreter}
        self.dataDictList().append(scriptDict)
        self.modified = True

    def removeScript(self, row):
        """
        Remove the script at `row`. Will not be removed from the
        Kickstart file until `commitChanges()` is called.
        """
        scriptDict = self.dataDict(row)
        if scriptDict[self.ColumnKeys[self.NameColumn]] != self.NewScriptName:
            self._scriptsToRemove.append(scriptDict)
        del self.dataDictList()[row]
        self.modified = True
