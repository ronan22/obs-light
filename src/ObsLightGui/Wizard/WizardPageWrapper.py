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
Created on 19 déc. 2011

@author: Florent Vennetier
'''

import imp
from os.path import dirname

from PySide.QtCore import Qt
from PySide.QtGui import QWizardPage

from ObsLightGui.ObsLightGuiObject import ObsLightGuiObject

class WizardPageWrapper(QWizardPage):
    '''
    QWizardPage wrapper to make duck punching available.
    '''

    def __init__(self, parent=None):
        QWizardPage.__init__(self, parent)


class ObsLightWizardPage(QWizardPage, ObsLightGuiObject):

    ui_WizardPage = None
    index = -1

    def __init__(self, gui, index, uiFileName, parent=None):
        QWizardPage.__init__(self, parent)
        ObsLightGuiObject.__init__(self, gui)
        self.index = index
        self.loadPageFromPyFile(uiFileName)

    def loadPageFromPyFile(self, name):
        u"""
        Load a wizard page from a '.py' file generated from a '.ui' file.
        This allows 'duck punching' on methods (because the loaded object
        is not directly a C++ object).
        """
        # clean module name
        if name.endswith(u".ui") or name.endswith(u".py"):
            name = name[:-3]
        # wizard modules should be in same directory as this module
        paths = [dirname(__file__)]
        # load the module
        file1, pathname, description = imp.find_module(name, paths)
        mod = imp.load_module(name, file1, pathname, description)
        # instantiate the class that will configure our wizard page
        # (they have all the same name: 'Ui_WizardPage')
        self.ui_WizardPage = mod.Ui_WizardPage()
        self.ui_WizardPage.setupUi(self)

    def setBusyCursor(self, func, *args, **kwargs):
        u"""
        Disable current page and set the cursor to WaitCursor
        while running `func` with `args` and `kwargs`.
        """
        cursor = self.wizard().cursor()
        self.setEnabled(False)
        self.wizard().setCursor(Qt.WaitCursor)
        try:
            return func(*args, **kwargs)
        finally:
            self.wizard().setCursor(cursor)
            self.setEnabled(True)
