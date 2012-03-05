# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseServer.ui'
#
# Created: Mon Mar  5 15:48:25 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtGui.QVBoxLayout(WizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.addNewServerButton = QtGui.QRadioButton(WizardPage)
        self.addNewServerButton.setChecked(True)
        self.addNewServerButton.setObjectName("addNewServerButton")
        self.verticalLayout.addWidget(self.addNewServerButton)
        self.chooseServerButton = QtGui.QRadioButton(WizardPage)
        self.chooseServerButton.setObjectName("chooseServerButton")
        self.verticalLayout.addWidget(self.chooseServerButton)
        self.serverListWidget = QtGui.QListWidget(WizardPage)
        self.serverListWidget.setEnabled(False)
        self.serverListWidget.setObjectName("serverListWidget")
        self.verticalLayout.addWidget(self.serverListWidget)

        self.retranslateUi(WizardPage)
        QtCore.QObject.connect(self.chooseServerButton, QtCore.SIGNAL("toggled(bool)"), self.serverListWidget.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "You can configure a new server or choose on from the list.", None, QtGui.QApplication.UnicodeUTF8))
        self.addNewServerButton.setText(QtGui.QApplication.translate("WizardPage", "Add new server", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseServerButton.setText(QtGui.QApplication.translate("WizardPage", "Choose from list:", None, QtGui.QApplication.UnicodeUTF8))

