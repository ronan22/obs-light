# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_newProject.ui'
#
# Created: Tue Dec 18 10:43:53 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.formLayout = QtGui.QFormLayout(WizardPage)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.projectNameLineEdit = QtGui.QLineEdit(WizardPage)
        self.projectNameLineEdit.setObjectName("projectNameLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.projectNameLineEdit)
        self.projectTitleLineEdit = QtGui.QLineEdit(WizardPage)
        self.projectTitleLineEdit.setObjectName("projectTitleLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.projectTitleLineEdit)
        self.projectDescriptionTextEdit = QtGui.QPlainTextEdit(WizardPage)
        self.projectDescriptionTextEdit.setObjectName("projectDescriptionTextEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.projectDescriptionTextEdit)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "New project", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Enter a name for the new project. You can also enter a title and a description (optional but recommended).", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Project name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Description:", None, QtGui.QApplication.UnicodeUTF8))

