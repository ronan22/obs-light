# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseTarget.ui'
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
        self.targetComboBox = QtGui.QComboBox(WizardPageWrapper)
        self.targetComboBox.setObjectName("targetComboBox")
        self.verticalLayout.addWidget(self.targetComboBox)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Target selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "Choose a target for the project.", None, QtGui.QApplication.UnicodeUTF8))

