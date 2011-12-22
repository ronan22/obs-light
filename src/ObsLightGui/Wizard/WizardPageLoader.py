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

from ObsLightGui.ObsLightGuiObject import ObsLightGuiObject
from WizardPageWrapper import WizardPageWrapper

def _fixExtension(source, old, new):
    if source.endswith(old):
        return source.replace(old, new)
    elif not source.endswith(new):
        return source + new
    else:
        return source

# TODO: try to merge WizardPageLoader and WizardPageWrapper
class WizardPageLoader(ObsLightGuiObject):
    _gui = None
    _page = None

    def __init__(self, gui, pageFileName, fromUiFile=False):
        ObsLightGuiObject.__init__(self, gui)
        if fromUiFile:
            self.loadPageFromUiFile(pageFileName)
        else:
            self.loadPageFromPyFile(pageFileName)

    def loadPageFromUiFile(self, name):
        u"""
        Load a wizard page from '.ui' file using `QtUiTools.QUiLoader`.
        """
        name = _fixExtension(name, u".py", u".ui")
        self.page = self.gui.loadWindow(name)

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
        # create a dummy wizard page
        self.page = WizardPageWrapper(None)
        # instantiate the class that will configure our wizard page
        # (they have all the same name: 'Ui_WizardPage')
        uiWP = mod.Ui_WizardPage()
        uiWP.setupUi(self.page)

    def waitWhile(self, func, *args, **kwargs):
        u"""
        Disables wizard page and sets cursor to WaitCursor
        while calling func.
        """
        cursor = self.page.wizard().cursor()
        self.page.setEnabled(False)
        self.page.wizard().setCursor(Qt.WaitCursor)
        try:
            return func(*args, **kwargs)
        finally:
            self.page.wizard().setCursor(cursor)
            self.page.setEnabled(True)

    @property
    def page(self): # pylint: disable-msg=E0202
        return self._page

    @page.setter # pylint: disable-msg=E1101
    def page(self, value): # pylint: disable-msg=E0202,E0102
        self._page = value
