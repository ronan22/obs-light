# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseTarget.ui'
#
# Created: Tue Sep 18 14:10:28 2012
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
        self.targetComboBox = QtGui.QComboBox(WizardPage)
        self.targetComboBox.setObjectName("targetComboBox")
        self.verticalLayout.addWidget(self.targetComboBox)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Target selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Choose a target for the project.", None, QtGui.QApplication.UnicodeUTF8))

