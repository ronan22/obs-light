# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProject.ui'
#
# Created: Thu Dec 22 16:48:06 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.8
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.formLayout = QtGui.QFormLayout(WizardPage)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.filterLineEdit = QtGui.QLineEdit(WizardPage)
        self.filterLineEdit.setObjectName("filterLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.filterLineEdit)
        self.projectListWidget = QtGui.QListWidget(WizardPage)
        self.projectListWidget.setObjectName("projectListWidget")
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.projectListWidget)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Project selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Select a project to import.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Filter:", None, QtGui.QApplication.UnicodeUTF8))

