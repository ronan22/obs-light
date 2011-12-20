# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configServerAlias.ui'
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
        self.formLayout = QtGui.QFormLayout(WizardPageWrapper)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtGui.QLabel(WizardPageWrapper)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_2)
        self.aliasLineEdit = QtGui.QLineEdit(WizardPageWrapper)
        self.aliasLineEdit.setObjectName("aliasLineEdit")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.aliasLineEdit)
        self.label = QtGui.QLabel(WizardPageWrapper)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.webUrlLabel = QtGui.QLabel(WizardPageWrapper)
        self.webUrlLabel.setObjectName("webUrlLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.webUrlLabel)
        self.label_4 = QtGui.QLabel(WizardPageWrapper)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_4)
        self.apiUrlLabel = QtGui.QLabel(WizardPageWrapper)
        self.apiUrlLabel.setObjectName("apiUrlLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.apiUrlLabel)
        self.label_6 = QtGui.QLabel(WizardPageWrapper)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_6)
        self.repositoryUrlLabel = QtGui.QLabel(WizardPageWrapper)
        self.repositoryUrlLabel.setObjectName("repositoryUrlLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.repositoryUrlLabel)
        self.label_8 = QtGui.QLabel(WizardPageWrapper)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_8)
        self.usernameLabel = QtGui.QLabel(WizardPageWrapper)
        self.usernameLabel.setObjectName("usernameLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.usernameLabel)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "Check your settings and enter an alias for this server.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPageWrapper", "Server alias:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPageWrapper", "Web URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.webUrlLabel.setText(QtGui.QApplication.translate("WizardPageWrapper", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPageWrapper", "API URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.apiUrlLabel.setText(QtGui.QApplication.translate("WizardPageWrapper", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("WizardPageWrapper", "Repository URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.repositoryUrlLabel.setText(QtGui.QApplication.translate("WizardPageWrapper", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("WizardPageWrapper", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.usernameLabel.setText(QtGui.QApplication.translate("WizardPageWrapper", "toto", None, QtGui.QApplication.UnicodeUTF8))

