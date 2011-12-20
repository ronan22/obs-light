# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseServer.ui'
#
# Created: Tue Dec 20 09:23:03 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.8
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPageWrapper):
        WizardPageWrapper.setObjectName("WizardPageWrapper")
        WizardPageWrapper.resize(400, 300)
        WizardPageWrapper.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtGui.QVBoxLayout(WizardPageWrapper)
        self.verticalLayout.setObjectName("verticalLayout")
        self.addNewServerButton = QtGui.QRadioButton(WizardPageWrapper)
        self.addNewServerButton.setChecked(True)
        self.addNewServerButton.setObjectName("addNewServerButton")
        self.verticalLayout.addWidget(self.addNewServerButton)
        self.chooseServerButton = QtGui.QRadioButton(WizardPageWrapper)
        self.chooseServerButton.setObjectName("chooseServerButton")
        self.verticalLayout.addWidget(self.chooseServerButton)
        self.serverListWidget = QtGui.QListWidget(WizardPageWrapper)
        self.serverListWidget.setEnabled(False)
        self.serverListWidget.setObjectName("serverListWidget")
        self.verticalLayout.addWidget(self.serverListWidget)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QObject.connect(self.chooseServerButton, QtCore.SIGNAL("toggled(bool)"), self.serverListWidget.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "You can configure a new server or choose on from the list.", None, QtGui.QApplication.UnicodeUTF8))
        self.addNewServerButton.setText(QtGui.QApplication.translate("WizardPageWrapper", "Add new server", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseServerButton.setText(QtGui.QApplication.translate("WizardPageWrapper", "Choose from list:", None, QtGui.QApplication.UnicodeUTF8))

