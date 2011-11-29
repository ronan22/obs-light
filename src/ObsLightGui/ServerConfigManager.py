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
Created on 17 nov. 2011

@author: Florent Vennetier
'''

from PySide.QtCore import QObject, QRegExp, Signal
from PySide.QtGui import QColor, QDialog, QDialogButtonBox, QGraphicsColorizeEffect
from PySide.QtGui import QLineEdit, QPushButton, QRegExpValidator

from ObsLight.ObsLightTools import isNonEmptyString

from Utils import popupOnException

class ServerConfigManager(QObject):
    '''
    Manage an OBS server configuration window.
    '''
    __gui = None
    __serverAlias = None
    __srvConfDialog = None
    __checkConnectionButton = None

    __dialogButtonBox = None
    __webUrlLineEdit = None
    __apiUrlLineEdit = None
    __repoUrlLineEdit = None
    __aliasLineEdit = None
    __userLineEdit = None
    __passLineEdit = None

    finished = Signal(bool)

    def __init__(self, gui, serverAlias=None):
        '''
        Load the server configuration window.
        If serverAlias is None, load an empty configuration.
        If serverAlias is an OBS server alias, load its configuration.
        '''
        QObject.__init__(self)
        self.__gui = gui
        self.__serverAlias = serverAlias
        self.__srvConfDialog = self.__gui.loadWindow(u"obsServerConfig.ui")
        self.__loadFieldObjects()
        if self.__serverAlias is not None:
            self.__loadInitialFieldValues()
        self.__srvConfDialog.finished.connect(self.on_obsServerConfigDialog_finished)
        self.__srvConfDialog.show()

    def __loadFieldObjects(self):
        self.__dialogButtonBox = self.__srvConfDialog.findChild(QDialogButtonBox,
                                                                "obsServerConfigButtonBox")
        self.disableOkButton()
        self.__webUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               u"serverWebUrlLineEdit")
        httpValidator = QRegExpValidator()
        httpValidator.setRegExp(QRegExp(u"http[s]?://.+"))
        self.__webUrlLineEdit.setValidator(httpValidator)
        self.__webUrlLineEdit.setPlaceholderText(u"http://myObs")
        self.__webUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__apiUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                               u"serverApiLineEdit")
        self.__apiUrlLineEdit.setValidator(httpValidator)
        self.__apiUrlLineEdit.setPlaceholderText(u"http://myObs:81")
        self.__apiUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__repoUrlLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                                u"serverRepoLineEdit")
        self.__repoUrlLineEdit.setValidator(httpValidator)
        self.__repoUrlLineEdit.setPlaceholderText(u"http://myObs:82")
        self.__repoUrlLineEdit.textEdited.connect(self.disableOkButton)
        self.__aliasLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                              u"serverAliasLineEdit")
        noSpaceValidator = QRegExpValidator()
        noSpaceValidator.setRegExp(QRegExp(u"\\S+"))
        self.__aliasLineEdit.setValidator(noSpaceValidator)
        self.__userLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                             u"usernameLineEdit")
        self.__passLineEdit = self.__srvConfDialog.findChild(QLineEdit,
                                                             u"passwordLineEdit")
        self.__checkConnectionButton = self.__srvConfDialog.findChild(QPushButton,
                                                                      u"checkConnectionButton")
        self.__checkConnectionButton.clicked.connect(self.on_checkConnectionButton_clicked)

    def __loadInitialFieldValues(self):
        manager = self.__gui.getObsLightManager()
        self.__aliasLineEdit.setText(self.__serverAlias)
        self.__aliasLineEdit.setReadOnly(True)
        self.__webUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                    u"serverWeb"))
        self.__apiUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                    u"serverAPI"))
        self.__repoUrlLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                     u"serverRepo"))
        self.__userLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                  u"user"))
        self.__passLineEdit.setText(manager.getObsServerParameter(self.__serverAlias,
                                                                  u"passw"))

    def getWebIfaceUrl(self):
        return self.__webUrlLineEdit.text()

    def getApiUrl(self):
        return self.__apiUrlLineEdit.text()

    def getRepoUrl(self):
        return self.__repoUrlLineEdit.text()

    def getAlias(self):
        return self.__aliasLineEdit.text()

    def getUser(self):
        return self.__userLineEdit.text()

    def getPass(self):
        return self.__passLineEdit.text()

    @popupOnException
    def on_obsServerConfigDialog_finished(self, result):
        # User canceled, nothing to do.
        if result == QDialog.Rejected:
            self.finished.emit(False)
        # User accepted, and there was no preloaded server,
        # so create a new server.
        elif self.__serverAlias is None:
            manager = self.__gui.getObsLightManager()
            manager.addObsServer(self.getApiUrl(),
                                 self.getUser(),
                                 self.getPass(),
                                 serverRepo=self.getRepoUrl(),
                                 alias=self.getAlias(),
                                 serverWeb=self.getWebIfaceUrl())
            self.finished.emit(True)
        # User accepted, and there was a preloaded server,
        # so modify it.
        else:
            manager = self.__gui.getObsLightManager()
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverWeb",
                                          self.getWebIfaceUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverAPI",
                                          self.getApiUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"serverRepo",
                                          self.getRepoUrl())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"user",
                                          self.getUser())
            manager.setObsServerParameter(self.__serverAlias,
                                          u"passw",
                                          self.getPass())
            self.finished.emit(True)

    def disableOkButton(self, _=None):
        # We need a parameter ^ in order to call this method from textEdited signal
        self.__dialogButtonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    @popupOnException
    def on_checkConnectionButton_clicked(self):
        def testAndColorizeUrl(url, widget, user=None, password=None):
            obsLightManager = self.__gui.getObsLightManager()
            color = u"pink"
            isOk = False
            try:
                if not isNonEmptyString(url):
                    color = u"red"
                elif obsLightManager.testUrl(url):
                    isOk = True
                    color = u"green"
                elif obsLightManager.testHost(url):
                    # Should not be OK, but at the moment we can't pass
                    # user and password so we may fall in this case
                    # whereas everything is fine.
                    isOk = True
                    color = u"green"
                    #color = u"orange"
                else:
                    color = u"red"
            except BaseException as e:
                print e
            effect = QGraphicsColorizeEffect(widget)
            effect.setColor(QColor(color))
            widget.setGraphicsEffect(effect)
            return isOk

        def testAndColorizeString(theString, widget):
            isOk = isNonEmptyString(theString)
            effect = QGraphicsColorizeEffect(widget)
            effect.setColor(QColor("green" if isOk else "red"))
            widget.setGraphicsEffect(effect)
            return isOk

        web = self.getWebIfaceUrl()
        api = self.getApiUrl()
        repo = self.getRepoUrl()


        allOk = testAndColorizeUrl(web, self.__webUrlLineEdit)
        # allOk MUST be second member, otherwise testAndColorizeUrl won't be
        # executed if the first call returns False
        allOk = testAndColorizeUrl(api, self.__apiUrlLineEdit) and allOk
        allOk = testAndColorizeUrl(repo, self.__repoUrlLineEdit) and allOk
        allOk = testAndColorizeString(self.getUser(), self.__userLineEdit) and allOk
        allOk = testAndColorizeString(self.getPass(), self.__passLineEdit) and allOk

        srvList = self.__gui.getObsLightManager().getObsServerList()
        effect = QGraphicsColorizeEffect(self.__aliasLineEdit)
        if self.getAlias() == self.__serverAlias or self.getAlias() not in srvList:
            effect.setColor(QColor("green"))
        else:
            effect.setColor(QColor("red"))
            allOk = False
        self.__aliasLineEdit.setGraphicsEffect(effect)

        self.__dialogButtonBox.button(QDialogButtonBox.Ok).setEnabled(allOk)
