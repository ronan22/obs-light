# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_newPackage.ui'
#
# Created: Wed Oct  3 19:10:30 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
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
        self.packageNameLineEdit = QtGui.QLineEdit(WizardPage)
        self.packageNameLineEdit.setObjectName("packageNameLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.packageNameLineEdit)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.packageTitleLineEdit = QtGui.QLineEdit(WizardPage)
        self.packageTitleLineEdit.setObjectName("packageTitleLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.packageTitleLineEdit)
        self.packageDescriptionTextEdit = QtGui.QPlainTextEdit(WizardPage)
        self.packageDescriptionTextEdit.setObjectName("packageDescriptionTextEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.packageDescriptionTextEdit)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "New package", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Enter a name for the new package. You can also enter a title and a description (optional but recommended).", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Package name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Description:", None, QtGui.QApplication.UnicodeUTF8))

