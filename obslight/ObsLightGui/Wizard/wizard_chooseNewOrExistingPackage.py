# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseNewOrExistingPackage.ui'
#
# Created: Wed Sep  5 11:04:14 2012
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
        self.importExistingPackageButton = QtGui.QRadioButton(WizardPage)
        self.importExistingPackageButton.setChecked(True)
        self.importExistingPackageButton.setObjectName("importExistingPackageButton")
        self.verticalLayout.addWidget(self.importExistingPackageButton)
        self.createNewPackageButton = QtGui.QRadioButton(WizardPage)
        self.createNewPackageButton.setObjectName("createNewPackageButton")
        self.verticalLayout.addWidget(self.createNewPackageButton)
        self.copyPackageButton = QtGui.QRadioButton(WizardPage)
        self.copyPackageButton.setEnabled(True)
        self.copyPackageButton.setToolTip("")
        self.copyPackageButton.setCheckable(True)
        self.copyPackageButton.setObjectName("copyPackageButton")
        self.verticalLayout.addWidget(self.copyPackageButton)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Import packages", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Do you want to import an existing package from server, create a new one from scratch, or branch an existing package on server ?", None, QtGui.QApplication.UnicodeUTF8))
        self.importExistingPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Import existing package", None, QtGui.QApplication.UnicodeUTF8))
        self.createNewPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Create new package", None, QtGui.QApplication.UnicodeUTF8))
        self.copyPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Copy of an existing package", None, QtGui.QApplication.UnicodeUTF8))

