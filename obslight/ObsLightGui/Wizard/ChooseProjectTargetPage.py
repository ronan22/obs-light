# -*- coding: utf8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
'''
Created on 21 déc. 2011

@author: Florent Vennetier
'''

from ObsLightGui.Utils import ProgressRunnable2

from WizardPageWrapper import ObsLightWizardPage

class ChooseProjectTargetPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_chooseTarget.ui")
        self.registerField(u"targetCBox*", self.ui_WizardPage.targetComboBox)

    def initializePage(self):
        server = self.wizard().getSelectedServerAlias()
        project = self.wizard().getSelectedProject()
        self._asyncGetTargetList(server, project)

    def _fillTargetCBox(self, targetList):
        self.ui_WizardPage.targetComboBox.clear()
        if targetList is not None:
            self.ui_WizardPage.targetComboBox.addItems(targetList)

    def _getTargetList(self, server, project):
        return self.manager.getTargetList(server, project)

    def _asyncGetTargetList(self, server, project):
        progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setDialogMessage(u"Loading target list (may be long)")
        runnable.setRunMethod(self._getTargetList, server, project)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.finished[object].connect(self._fillTargetCBox)
        progress.forceShow()
        runnable.runOnGlobalInstance()

    def getSelectedTarget(self):
        return self.ui_WizardPage.targetComboBox.currentText()
