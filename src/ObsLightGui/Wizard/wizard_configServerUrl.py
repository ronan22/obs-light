# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configServerUrl.ui'
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
        WizardPageWrapper.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.formLayout = QtGui.QFormLayout(WizardPageWrapper)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPageWrapper)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.webUrlLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.webUrlLineEdit.setObjectName("webUrlLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.webUrlLineEdit)
        self.apiUrlLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.apiUrlLineEdit.setObjectName("apiUrlLineEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.apiUrlLineEdit)
        self.repoUrlLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.repoUrlLineEdit.setObjectName("repoUrlLineEdit")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.repoUrlLineEdit)
        self.label_2 = QtGui.QLabel(WizardPageWrapper)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(WizardPageWrapper)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "Enter the 3 URL required to access this server.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPageWrapper", "Web interface URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPageWrapper", "API URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPageWrapper", "Repository URL:", None, QtGui.QApplication.UnicodeUTF8))

