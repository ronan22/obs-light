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
Created on 17 avr. 2012

@author: Florent Vennetier
'''

from WizardPageWrapper import ObsLightWizardPage

class ConfigureNewProjectPage(ObsLightWizardPage):

    def __init__(self, gui, index):
        ObsLightWizardPage.__init__(self, gui, index, u"wizard_newProject.ui")

        self.registerField(u"newProjectName*",
                           self.ui_WizardPage.projectNameLineEdit)
        self.registerField(u"newProjectTitle",
                           self.ui_WizardPage.projectTitleLineEdit)
        self.registerField(u"newProjectDescription",
                           self.ui_WizardPage.projectDescriptionTextEdit)

    def cleanupPage(self):
        pass

    def validatePage(self):
        newPrjName = self.field(u"newProjectName")
        newPrjTitle = self.field(u"newProjectTitle")
        newPrjDescr = self.field(u"newProjectDescription")
        serverAlias = self.field(u"serverAlias")
        retVal = self._createProject(serverAlias,
                                     newPrjName,
                                     newPrjTitle,
                                     newPrjDescr)
        return retVal is not None

    def _createProject(self, server, name, title, description):
        retVal = self.callWithInfiniteProgress(self.manager.createObsProject,
                                               "Creating project %s" % name,
                                               server,
                                               name,
                                               title,
                                               description)
        return retVal
