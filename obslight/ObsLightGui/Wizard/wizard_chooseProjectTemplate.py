# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProjectTemplate.ui'
#
# Created: Wed Sep 19 15:56:27 2012
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
        self.addNewLocalProjectButton = QtGui.QRadioButton(WizardPage)
        self.addNewLocalProjectButton.setChecked(True)
        self.addNewLocalProjectButton.setObjectName("addNewLocalProjectButton")
        self.verticalLayout.addWidget(self.addNewLocalProjectButton)
        self.chooseNewLocalProjectButton = QtGui.QRadioButton(WizardPage)
        self.chooseNewLocalProjectButton.setObjectName("chooseNewLocalProjectButton")
        self.verticalLayout.addWidget(self.chooseNewLocalProjectButton)
        self.LocalProjectListWidget = QtGui.QListWidget(WizardPage)
        self.LocalProjectListWidget.setEnabled(False)
        self.LocalProjectListWidget.setObjectName("LocalProjectListWidget")
        self.verticalLayout.addWidget(self.LocalProjectListWidget)

        self.retranslateUi(WizardPage)
        QtCore.QObject.connect(self.chooseNewLocalProjectButton, QtCore.SIGNAL("toggled(bool)"), self.LocalProjectListWidget.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Local Project configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "You can configure a new local project or choose on from the list.", None, QtGui.QApplication.UnicodeUTF8))
        self.addNewLocalProjectButton.setText(QtGui.QApplication.translate("WizardPage", "new Local Project", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseNewLocalProjectButton.setText(QtGui.QApplication.translate("WizardPage", "Choose Local Project from list:", None, QtGui.QApplication.UnicodeUTF8))

