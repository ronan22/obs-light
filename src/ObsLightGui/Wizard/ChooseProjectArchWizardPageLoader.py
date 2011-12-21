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

from PySide.QtGui import QComboBox

from ObsLightGui.Utils import uiFriendly

from WizardPageLoader import WizardPageLoader
import ConfigWizard

class ChooseProjectArchWizardPageLoader(WizardPageLoader):

    def __init__(self, gui):
        WizardPageLoader.__init__(self, gui, u"wizard_chooseArchitecture.ui")
        self.archCBox = self.page.findChild(QComboBox, u"architectureComboBox")
        self.page.registerField(u"archCBox*", self.archCBox)
        self.page.initializePage = self._initializePage
        self.page.getSelectedArch = self.getSelectedArch
        self.page.setCommitPage(True)

    def _initializePage(self):
        server = self.page.field(u"serverAlias")
        chooseProjectPageIndex = ConfigWizard.ConfigWizard.pageIndex(u'ChooseProject')
        chooseProjectPage = self.page.wizard().page(chooseProjectPageIndex)
        project = chooseProjectPage.getSelectedProject()
        chooseTargetPageIndex = ConfigWizard.ConfigWizard.pageIndex(u'ChooseProjectTarget')
        chooseTargetPage = self.page.wizard().page(chooseTargetPageIndex)
        target = chooseTargetPage.getSelectedTarget()
        self.waitWhile(self._fillArchCBox, server, project, target)

    def _fillArchCBox(self, server, project, target):
        self.archCBox.clear()
        archList = self._getArchList(server, project, target)
        self.archCBox.addItems(archList)

    @uiFriendly()
    def _getArchList(self, server, project, target):
        return self.manager.getArchitectureList(server, project, target)

    def getSelectedArch(self):
        return self.archCBox.currentText()
