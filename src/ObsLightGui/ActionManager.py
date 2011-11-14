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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
'''
Created on 27 oct. 2011

@author: Florent Vennetier
'''

from PySide.QtGui import QAction, QMessageBox

from ServerManager import ServerListManager

class MainWindowActionManager(object):
    '''
    Manage the action menu of the main window.
    Connects the actions signals to the appropriate slots.
    '''
    __gui = None
    __obsLightManager = None
    __serverListManager = None

    def __init__(self, gui):
        self.__gui = gui
        self.__obsLightManager = self.__gui.getObsLightManager()
        mainWindow = self.__gui.getMainWindow()
        actionOBS_servers = mainWindow.findChild(QAction, "actionOBS_servers")
        actionOBS_servers.triggered.connect(self.on_actionOBS_servers_triggered)
        actionAbout_Qt = mainWindow.findChild(QAction, "actionAbout_Qt")
        actionAbout_Qt.triggered.connect(self.on_actionAbout_qt_triggered)
        actionAbout = mainWindow.findChild(QAction, "actionAbout")
        actionAbout.triggered.connect(self.on_actionAbout_triggered)
        
    def on_actionOBS_servers_triggered(self):
        self.__serverListManager = ServerListManager(self.__gui)

    def on_actionAbout_qt_triggered(self):
        QMessageBox.aboutQt(self.__gui.getMainWindow())

    def on_actionAbout_triggered(self):
        QMessageBox.about(self.__gui.getMainWindow(), "About OBS Light",
            "OBS Light, a lighter version of OBS.<br /><br />"
            + "The full description of OBS Light can be found at "
            + "<a href=\"http://wiki.meego.com/OBS_Light\">http://wiki.meego.com/OBS_Light</a><br />"
            + "and the FAQ is at <a href=\"http://wiki.meego.com/OBS_Light_FAQ\">http://wiki.meego.com/OBS_Light_FAQ</a>")
