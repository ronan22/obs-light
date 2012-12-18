# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_choosePackage.ui'
#
# Created: Tue Dec 18 10:43:52 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.filterLineEdit = QtGui.QLineEdit(WizardPage)
        self.filterLineEdit.setObjectName("filterLineEdit")
        self.gridLayout.addWidget(self.filterLineEdit, 0, 1, 1, 1)
        self.packageListWidget = QtGui.QListWidget(WizardPage)
        self.packageListWidget.setObjectName("packageListWidget")
        self.gridLayout.addWidget(self.packageListWidget, 1, 0, 1, 2)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Package selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Select packages to import.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Filter:", None, QtGui.QApplication.UnicodeUTF8))

