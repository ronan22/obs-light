# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configServerUrl.ui'
#
# Created: Wed May 16 09:56:48 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(405, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.formLayout = QtGui.QFormLayout(WizardPage)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.webUrlLineEdit = QtGui.QLineEdit(WizardPage)
        self.webUrlLineEdit.setObjectName("webUrlLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.webUrlLineEdit)
        self.apiUrlLineEdit = QtGui.QLineEdit(WizardPage)
        self.apiUrlLineEdit.setObjectName("apiUrlLineEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.apiUrlLineEdit)
        self.repoUrlLineEdit = QtGui.QLineEdit(WizardPage)
        self.repoUrlLineEdit.setObjectName("repoUrlLineEdit")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.repoUrlLineEdit)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label_3)
        self.label_5 = QtGui.QLabel(WizardPage)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(9, QtGui.QFormLayout.LabelRole, self.label_5)
        self.label_4 = QtGui.QLabel(WizardPage)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(10, QtGui.QFormLayout.LabelRole, self.label_4)
        self.usernameLineEdit = QtGui.QLineEdit(WizardPage)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.usernameLineEdit)
        self.passwordLineEdit = QtGui.QLineEdit(WizardPage)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.passwordLineEdit)
        self.line = QtGui.QFrame(WizardPage)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(7, QtGui.QFormLayout.SpanningRole, self.line)
        self.label_6 = QtGui.QLabel(WizardPage)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(11, QtGui.QFormLayout.FieldRole, self.label_6)
        self.label_7 = QtGui.QLabel(WizardPage)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.label_7)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Server configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Enter the 3 URL required to access this server, your user name and your password. These will be checked before going to the next page.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Web interface URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "API URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Repository URL:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("WizardPage", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("WizardPage", "Green  -->  OK\n"
"Red  -->  Wrong username or password\n"
"Orange  -->  cannot test due to URL error", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("WizardPage", "Green  -->  OK\n"
"Red  -->  Error\n"
"Orange  -->  Host OK but wrong URL", None, QtGui.QApplication.UnicodeUTF8))

