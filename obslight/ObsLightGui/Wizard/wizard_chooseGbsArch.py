# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseGbsArch.ui'
#
# Created: Wed Oct  3 19:10:28 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.horizontalLayout = QtGui.QHBoxLayout(WizardPage)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.LocalTargetListcomboBox = QtGui.QComboBox(WizardPage)
        self.LocalTargetListcomboBox.setObjectName("LocalTargetListcomboBox")
        self.horizontalLayout.addWidget(self.LocalTargetListcomboBox)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Arch selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Choose an  Arch for the project.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Choose the project  Arch:", None, QtGui.QApplication.UnicodeUTF8))

