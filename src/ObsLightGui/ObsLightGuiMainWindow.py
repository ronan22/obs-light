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
Created on 2 mars 2012

@author: Florent Vennetier
'''

from PySide.QtGui import QMainWindow

class ObsLightGuiMainWindow(QMainWindow):
    """
    `QtGui.QMainWindow` subclass which adds possibility to call
    functions before it is closed. You just have to call
    `mainWindow.callBeforeCloseEvent.append(yourFunc)`
    and `yourFunc` will be called just before the `QtGui.QCloseEvent`
    is handled.
    """

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.callBeforeCloseEvent = []

    def closeEvent(self, event):
        for func in self.callBeforeCloseEvent:
            func()
        super(ObsLightGuiMainWindow, self).closeEvent(event)
