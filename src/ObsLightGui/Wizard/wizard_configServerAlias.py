# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configServerAlias.ui'
#
# Created: Mon Mar  5 15:48:25 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.formLayout = QtGui.QFormLayout(WizardPage)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_2)
        self.aliasLineEdit = QtGui.QLineEdit(WizardPage)
        self.aliasLineEdit.setObjectName("aliasLineEdit")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.aliasLineEdit)
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.webUrlLabel = QtGui.QLabel(WizardPage)
        self.webUrlLabel.setObjectName("webUrlLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.webUrlLabel)
        self.label_4 = QtGui.QLabel(WizardPage)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_4)
        self.apiUrlLabel = QtGui.QLabel(WizardPage)
        self.apiUrlLabel.setObjectName("apiUrlLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.apiUrlLabel)
        self.label_6 = QtGui.QLabel(WizardPage)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_6)
        self.repoUrlLabel = QtGui.QLabel(WizardPage)
        self.repoUrlLabel.setObjectName("repoUrlLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.repoUrlLabel)
        self.label_8 = QtGui.QLabel(WizardPage)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_8)
        self.usernameLabel = QtGui.QLabel(WizardPage)
        self.usernameLabel.setObjectName("usernameLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.usernameLabel)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.label_3)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Check your settings and enter an alias for this server.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Server alias:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Web URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.webUrlLabel.setText(QtGui.QApplication.translate("WizardPage", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "API URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.apiUrlLabel.setText(QtGui.QApplication.translate("WizardPage", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("WizardPage", "Repository URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.repoUrlLabel.setText(QtGui.QApplication.translate("WizardPage", "url", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("WizardPage", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.usernameLabel.setText(QtGui.QApplication.translate("WizardPage", "toto", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Green --> OK\n"
"Red --> Already in use", None, QtGui.QApplication.UnicodeUTF8))

