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

from Utils import ProgressRunnable2

class ObsLightGuiObject(object):

    _gui = None

    def __init__(self, gui):
        self._gui = gui

    @property
    def gui(self):
        return self._gui

    @property
    def manager(self):
        return self.gui.getObsLightManager()

    @property
    def mainWindow(self):
        return self.gui.getMainWindow()

    def callWithProgress(self, func, iterable, message, *args, **kwargs):
        runnable = ProgressRunnable2(self.gui.getProgressDialog())
        runnable.setFunctionToMap(func,
                                  iterable,
                                  message,
                                  *args,
                                  **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance(wait=True)
        return runnable.result

    def callWithInfiniteProgress(self, func, message, *args, **kwargs):
        runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
        runnable.setDialogMessage(message)
        runnable.setRunMethod(func, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance(wait=True)
        return runnable.result
