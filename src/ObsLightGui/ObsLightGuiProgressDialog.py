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
Created on 8 mars 2012

@author: Florent Vennetier
'''

from PySide.QtCore import Signal
from PySide.QtGui import QApplication, QDialog

class ObsLightGuiProgressDialog(QDialog):
    """
    Replacement for QProgressDialog which allows to load a custom
    design from an UI file.
    We did it because we wanted to add a "show log" button.
    `minimumDuration()` will return the value set by
    `setMinimumDuration()` but has no effect.
    """

    canceled = Signal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self._wasCanceled = False
        self._autoClose = True
        self._autoReset = True
        self._minimumDuration = 0
        self.canceled.connect(self.cancel)

    def autoClose(self):
        return self._autoClose

    def autoReset(self):
        return self._autoReset

    def labelText(self):
        return self.label.text()

    def maximum(self):
        return self.progressBar.maximum()

    def minimum(self):
        return self.progressBar.minimum()

    def minimumDuration(self):
        return self._minimumDuration

    def setAutoClose(self, close):
        self._autoClose = close

    def setAutoReset(self, reset):
        self._autoReset = reset

    def setBar(self, bar):
        self.progressBar = bar

    def setCancelButton(self, button):
        self.cancelButton = button

    def setLabel(self, label):
        self.label = label

    def value(self):
        return self.progressBar.value()

    def wasCanceled(self):
        return self._wasCanceled

    def cancel(self):
        self._wasCanceled = True
        self.reset()

    def forceShow(self):
        self.show()

    def reset(self):
        self.progressBar.reset()
        if self._autoClose:
            self.hide()
        self._wasCanceled = False

    def setCancelButtonText(self, text):
        self.cancelButton.setText(text)

    def setLabelText(self, text):
        self.label.setText(text)

    def setMaximum(self, maximum):
        self.progressBar.setMinimum(maximum)

    def setMinimum(self, minimum):
        self.progressBar.setMinimum(minimum)

    def setMinimumDuration(self, ms):
        self._minimumDuration = ms

    def setRange(self, minimum, maximum):
        self.progressBar.setRange(minimum, maximum)

    def setValue(self, progress):
        self.progressBar.setValue(progress)
        if self._autoReset and self.value() == self.maximum():
            self.reset()
        if self.isModal():
            QApplication.processEvents()

    def connectButtons(self):
        """
        Connect the cancel button to the canceled signal.
        """
        self.cancelButton.clicked.connect(self.canceled)

    def showCancelButton(self, visible=True):
        """
        Hide or show the cancel button.
        """
        self.cancelButton.setHidden(not visible)
