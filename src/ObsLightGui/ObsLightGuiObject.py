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
Created on 19 déc. 2011

@author: Florent Vennetier
'''

from Utils import ProgressRunnable2

class ObsLightGuiObject(object):
    """
    Provides "gui", "manager" and "mainWindow" properties.
    Provides "callWithProgress" and "callWithInfiniteProgress" methods.
    """

    def __init__(self, gui):
        self._gui = gui

    @property
    def gui(self):
        """
        Get a reference to the `ObsLightGui.Gui.Gui` instance.
        """
        return self._gui

    @property
    def manager(self):
        """
        Get a reference to the `ObsLight.ObsLightManager.ObsLightManager` instance.
        """
        return self.gui.manager

    @property
    def mainWindow(self):
        """
        Get a reference to the main window.
        """
        return self.gui.mainWindow

    def callWithProgress(self, func, iterable, message, *args, **kwargs):
        """
        Call `func(item, *args, **kwargs)`, with item being successively
        each element of `iterable`, while displaying a progress dialog.
        `message` is displayed in the progress dialog, and if it contains
        "%(arg)s", it is replaced by a string representation of the item
        being processed.
        """
        if len(iterable) > 1:
            progress = self.gui.getProgressDialog()
        else:
            progress = self.gui.getInfiniteProgressDialog()
        runnable = ProgressRunnable2(progress)
        runnable.setFunctionToMap(func,
                                  iterable,
                                  message,
                                  *args,
                                  **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance(wait=True)
        return runnable.result

    def callWithInfiniteProgress(self, func, message, *args, **kwargs):
        """
        Call `func(*args, **kwargs)` while displaying an infinite progress
        dialog with `message`.
        """
        runnable = ProgressRunnable2(self.gui.getInfiniteProgressDialog())
        runnable.setDialogMessage(message)
        runnable.setRunMethod(func, *args, **kwargs)
        runnable.caughtException.connect(self.gui.popupErrorCallback)
        runnable.runOnGlobalInstance(wait=True)
        return runnable.result
