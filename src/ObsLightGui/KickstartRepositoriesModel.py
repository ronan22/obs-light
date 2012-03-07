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

from PySide.QtCore import Qt
from KickstartModelBase import KickstartModelBase

class KickstartRepositoriesModel(KickstartModelBase):
    """
    Class to manage the repositories of the Kickstart file of a MIC project.
    """

    NameColumn = 0
    UrlColumn = 1
    PriorityColumn = 2
    SslVerifyColumn = 3
    GpgKeyColumn = 4
    DisableColumn = 5
    SaveColumn = 6
    IncludePkgsColumn = 7
    ExcludePkgsColumn = 8
    SourceColumn = 9
    DebugInfoColumn = 10


    # A tuple containing the keys of repository dictionaries
    ColumnKeys = ("name", "baseurl", "priority", "ssl_verify", "gpgkey", "disable",
                  "save", "includepkgs", "excludepkgs", "source", "debuginfo")

    ColumnHeaders = ("Name", "URL", "Priority", "SSL verif", "GPG key", "Enabled",
                     "Save", "Included packages", "Excluded packages", "Source", "Debug info")
    ColumnToolTips = ("A name for the repository, must be unique",
                      "The URL of the repository",
                      "The priority of the repository. 1 is the highest priority, " +
                        "the default is 99. You can let the field empty.",
                      "Do SSL verification for HTTPS repositories",
                      "The path (or URL) to the GPG key for this repository " +
                        "in the final filesystem",
                      "Uncheck to add the repository as disabled",
                      "Save the repository in the generated image",
                      "A comma-separated list of package names and globs" +
                        " that must be pulled from this repository",
                      "A comma-separated list of package names and globs" +
                        " that must not be pulled from this repository",
                      "Also add source packages repository",
                      "Also add debuginfo packages repository")

    def __init__(self, obsLightManager, projectName):
        """
        `obsLightManager`: a reference to the ObsLightManager instance
        `projectName`: the name of the MIC project to manage Kickstart commands
        """
        KickstartModelBase.__init__(self,
                                    obsLightManager,
                                    projectName,
                                    obsLightManager.getKickstartRepositoryDictionaries,
                                    self.ColumnKeys[self.NameColumn])

    # from QAbstractTableModel
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Vertical:
                return section
            else:
                return self.ColumnHeaders[section]
        elif role == Qt.ToolTipRole:
            return self.ColumnToolTips[section]
        return None

    # from QAbstractTableModel
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            # We double-clicking on cell (Qt.EditRole) we return
            # same data as on normal display
            return self.displayRoleData(index)
        elif role == Qt.CheckStateRole:
            return self.checkStateRoleData(index)
        return None

    # from QAbstractTableModel
    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        if role == Qt.EditRole:
            if value == self.displayRoleData(index):
                # nothing to do
                return False
            # convert empty strings and "none" to None
            if column == self.PriorityColumn:
                if isinstance(value, basestring) and (value.lower() == "none" or value == ""):
                    value = None
            elif column in (self.IncludePkgsColumn, self.ExcludePkgsColumn):
                value = value.strip()
                if len(value) < 1:
                    value = ""
                else:
                    value = [p.strip() for p in value.split(",")]
            # in case repository name has changed, we must keep the old name
            oldName = self.dataDict(row)[self.ColumnKeys[self.NameColumn]]
            # do the change in memory
            self.dataDict(row)[self.ColumnKeys[column]] = value
            # commit the change on disk
            self.__updateRepoInManager(row, oldName)
            # update the view
            self.refresh()
            return True
        elif role == Qt.CheckStateRole:
            # SslVerify parameter is stored as a string, not a boolean
            if column == self.SslVerifyColumn:
                if value == Qt.CheckState.Checked:
                    self.dataDict(row)[self.ColumnKeys[column]] = "yes"
                else:
                    self.dataDict(row)[self.ColumnKeys[column]] = "no"
            # The logic of these columns is inverted
            elif column in (self.DisableColumn,):
                self.dataDict(row)[self.ColumnKeys[column]] = (value != Qt.CheckState.Checked)
            # Other columns
            elif column in (self.SaveColumn, self.SourceColumn, self.DebugInfoColumn):
                self.dataDict(row)[self.ColumnKeys[column]] = (value == Qt.CheckState.Checked)
            oldName = self.dataDict(row)[self.ColumnKeys[self.NameColumn]]
            self.__updateRepoInManager(row, oldName)
        return False

    # from QAbstractTableModel
    def flags(self, index):
        """
        Calls `QAbstractTableModel.flags()` and add `Qt.ItemIsEditable` flag.
        In this model, all cells except column SslVerifyColumn are editable.
        Cells of column SslVerifyColumn are checkable.
        """
        superFlags = super(KickstartRepositoriesModel, self).flags(index)
        column = index.column()
        if column in (self.SslVerifyColumn, self.DisableColumn,
                              self.SaveColumn, self.SourceColumn, self.DebugInfoColumn):
            superFlags = superFlags | Qt.ItemIsUserCheckable
        else:
            superFlags = superFlags | Qt.ItemIsEditable
        return superFlags

    def displayRoleData(self, index):
        """
        Return the "Qt.DisplayRole" data for cell at `index`.
        """
        column = index.column()
        retVal = self.dataDict(index.row())[self.ColumnKeys[column]]
        if column in (self.SslVerifyColumn, self.DisableColumn,
                      self.SaveColumn, self.SourceColumn, self.DebugInfoColumn):
            return None
        elif column in (self.IncludePkgsColumn, self.ExcludePkgsColumn):
            retVal = ",".join(retVal)
        return retVal if retVal is None else str(retVal)

    def checkStateRoleData(self, index):
        """
        Return the `Qt.CheckStateRole` data for cell at `index`.
        Returning None for all columns, except SslVerifyColumn:
          Qt.CheckState.Checked if SSL verification is "yes",
          Qt.CheckState.Unchecked otherwise
        """
        column = index.column()
        # SslVerify parameter is stored as a string, not a boolean
        if column == self.SslVerifyColumn:
            verify = self.dataDict(index.row())[self.ColumnKeys[self.SslVerifyColumn]]
            return Qt.CheckState.Checked if verify.lower() == "yes" else Qt.CheckState.Unchecked
        # The logic of these columns is inverted
        elif column in (self.DisableColumn,):
            retVal = bool(self.dataDict(index.row())[self.ColumnKeys[column]])
            return Qt.CheckState.Unchecked if retVal else Qt.CheckState.Checked
        # Other columns
        elif column in (self.SaveColumn, self.SourceColumn, self.DebugInfoColumn):
            retVal = bool(self.dataDict(index.row())[self.ColumnKeys[column]])
            return Qt.CheckState.Checked if retVal else Qt.CheckState.Unchecked

        return None

    def __updateRepoInManager(self, row, oldName):
        """
        Remove the old repository,
        add the new one,
        flush the Kickstart file on disk.
        """
        repoDict = self.dataDict(row)
        self.manager.removeKickstartRepository(self.currentProject, oldName)
        # pylint: disable-msg=W0142
        self.manager.addKickstartRepository(self.currentProject, **repoDict)
        self.manager.saveKickstartFile(self.currentProject)

    def addRepository(self, name, url):
        """
        Add a repository `name` with `url`. Other repository parameters
        will have default values, and can be modified using `setData`.
        """
        sslVerify = "yes" if url.startswith("https") else "no"
        self.manager.addKickstartRepository(self.currentProject, baseurl=url,
                                            name=name,
                                            ssl_verify=sslVerify)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()

    def removeRepository(self, name):
        """
        Remove the repository `name` from the Kickstart file.
        """
        self.manager.removeKickstartRepository(self.currentProject, name)
        self.manager.saveKickstartFile(self.currentProject)
        self.refresh()
