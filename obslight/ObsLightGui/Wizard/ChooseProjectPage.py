# -*- coding: utf8 -*-
#
# Copyright 2011-2012, Intel Inc.
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
Created on 21 déc. 2011

@author: Florent Vennetier
'''
from PySide.QtGui import QMessageBox
from ObsLightGui.FilterableWidget import FilterableWidget
from ObsLightGui.Utils import popupOnException, ProgressRunnable2

from WizardPageWrapper import ObsLightWizardPage

class ChooseProjectPage(ObsLightWizardPage, FilterableWidget):
    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseProject.ui")
        uwp = self.ui_WizardPage
        FilterableWidget.__init__(self, uwp.filterLineEdit,
                                  uwp.projectListWidget)
        uwp.restrainMaintainerCheckBox.stateChanged.connect(self._checkBoxStateChanged)
        uwp.restrainBugownerCheckBox.stateChanged.connect(self._checkBoxStateChanged)
        uwp.restrainRemoteLinksCheckBox.stateChanged.connect(self._checkBoxStateChanged)
        self.registerField(u"projectRow*", uwp.projectListWidget)
        self.registerField(u"restrainMaintainer", uwp.restrainMaintainerCheckBox)
        self.registerField(u"restrainBugowner", uwp.restrainBugownerCheckBox)
        self.registerField(u"restrainRemoteLinks", uwp.restrainRemoteLinksCheckBox)

    def initializePage(self):
        serverAlias = self.wizard().getSelectedServerAlias()
        restrainMaintainer = self.field(u"restrainMaintainer")
        restrainBugowner = self.field(u"restrainBugowner")
        restrainRemoteLinks = self.field(u"restrainRemoteLinks")
        self._asyncFillProjectList(serverAlias,
                                   restrainMaintainer,
                                   restrainBugowner,
                                   restrainRemoteLinks)

    @popupOnException
    def validatePage(self):
        if not self.isComplete():
            return False
        readonly = self._isSelectedProjectReadOnly()
        if readonly:
            msg = u"Warning: the project you selected is read only!\n"
            msg += u"You won't be able to push modifications.\n\n"
            msg += u"Do you want to import it anyway?"
            result = QMessageBox.warning(self,
                                         u"Read only project",
                                         msg,
                                         buttons=QMessageBox.Yes | QMessageBox.Cancel,
                                         defaultButton=QMessageBox.Yes)
            return result == QMessageBox.Yes
        return True

    @popupOnException
    def _checkBoxStateChanged(self, _state):
        self.initializePage()

    def _getProjectList(self,
                        serverAlias,
                        restrainMaintainer,
                        restrainBugowner,
                        restrainRemoteLinks):
        """
        Retrieve project list from `serverAlias`.
        See `ObsLightManager.getObsServerProjectList` for the meaning of
        `restrainMaintainer`, `restrainBugowner` and `restrainRemoteLinks`
        """
        return self.manager.getObsServerProjectList(serverAlias,
                                                    maintainer=restrainMaintainer,
                                                    bugowner=restrainBugowner,
                                                    remoteurl=restrainRemoteLinks)

    def _fillProjectList(self, projectList):
        """
        Clear the project list widget and fill it with
        project names from `projectList`.
        """
        self.ui_WizardPage.projectListWidget.clear()
        if projectList is not None:
            self.ui_WizardPage.projectListWidget.addItems(projectList)

    def _asyncFillProjectList(self,
                              serverAlias,
                              restrainMaintainer,
                              restrainBugowner,
                              restrainRemoteLinks):
        """
        Asynchronously call `_getProjectList()` and send the results
        to `_fillProjectList()`.
        """
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Loading project list (may be long)")
        runnable.setRunMethod(self._getProjectList,
                              serverAlias,
                              restrainMaintainer,
                              restrainBugowner,
                              restrainRemoteLinks)

        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished[object].connect(self._fillProjectList)
        progress.forceShow()
        runnable.runOnGlobalInstance()

    def _isSelectedProjectReadOnly(self):
        """Checks if the selected project is readonly (with progress bar)"""
        project = str(self.getSelectedProject())
        server = str(self.wizard().getSelectedServerAlias())
        ro = self.callWithInfiniteProgress(self.manager.getObsProjectParameter,
                                           u"Checking if project '%s' is readonly" % project,
                                           server,
                                           project,
                                           "readonly")
        return ro

    def getSelectedProject(self):
        return self.ui_WizardPage.projectListWidget.item(self.field(u"projectRow")).text()
