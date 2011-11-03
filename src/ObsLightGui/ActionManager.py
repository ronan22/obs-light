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

from PySide.QtGui import QAction

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
        action = mainWindow.findChild(QAction, "actionOBS_servers")
        action.triggered.connect(self.on_actionOBS_servers_triggered)
        
    def on_actionOBS_servers_triggered(self):
        self.__serverListManager = ServerListManager(self.__gui)
