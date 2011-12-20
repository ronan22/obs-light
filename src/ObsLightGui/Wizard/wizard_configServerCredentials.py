# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configServerCredentials.ui'
#
# Created: Tue Dec 20 09:23:04 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.8
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPageWrapper):
        WizardPageWrapper.setObjectName("WizardPageWrapper")
        WizardPageWrapper.resize(400, 300)
        self.formLayout = QtGui.QFormLayout(WizardPageWrapper)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPageWrapper)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.usernameLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.usernameLineEdit)
        self.label_2 = QtGui.QLabel(WizardPageWrapper)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.passwordLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.passwordLineEdit)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "Enter your login and your password.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPageWrapper", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPageWrapper", "Password:", None, QtGui.QApplication.UnicodeUTF8))

