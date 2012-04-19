# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseNewOrExistingPackage.ui'
#
# Created: Thu Apr 19 09:00:09 2012
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
        self.branchPackageButton = QtGui.QRadioButton(WizardPage)
        self.branchPackageButton.setEnabled(False)
        self.branchPackageButton.setObjectName("branchPackageButton")
        self.verticalLayout.addWidget(self.branchPackageButton)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Import packages", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Do you want to import an existing package from server, create a new one from scratch, or branch an existing package on server ?", None, QtGui.QApplication.UnicodeUTF8))
        self.importExistingPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Import existing package", None, QtGui.QApplication.UnicodeUTF8))
        self.createNewPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Create new package", None, QtGui.QApplication.UnicodeUTF8))
        self.branchPackageButton.setToolTip(QtGui.QApplication.translate("WizardPage", "Not implemented", None, QtGui.QApplication.UnicodeUTF8))
        self.branchPackageButton.setText(QtGui.QApplication.translate("WizardPage", "Create a branch of an existing package", None, QtGui.QApplication.UnicodeUTF8))

