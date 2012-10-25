# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_newPackageFromGit.ui'
#
# Created: Mon Oct 22 16:44:51 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.packageNameLineEdit = QtGui.QLineEdit(WizardPage)
        self.packageNameLineEdit.setObjectName("packageNameLineEdit")
        self.gridLayout.addWidget(self.packageNameLineEdit, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(WizardPage)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.gitUrlLineEdit = QtGui.QLineEdit(WizardPage)
        self.gitUrlLineEdit.setObjectName("gitUrlLineEdit")
        self.gridLayout.addWidget(self.gitUrlLineEdit, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.packageTitleLineEdit = QtGui.QLineEdit(WizardPage)
        self.packageTitleLineEdit.setObjectName("packageTitleLineEdit")
        self.gridLayout.addWidget(self.packageTitleLineEdit, 3, 1, 1, 1)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.packageDescriptionTextEdit = QtGui.QPlainTextEdit(WizardPage)
        self.packageDescriptionTextEdit.setObjectName("packageDescriptionTextEdit")
        self.gridLayout.addWidget(self.packageDescriptionTextEdit, 5, 1, 1, 1)
        self.gitSubDirLineEdit = QtGui.QLineEdit(WizardPage)
        self.gitSubDirLineEdit.setObjectName("gitSubDirLineEdit")
        self.gridLayout.addWidget(self.gitSubDirLineEdit, 2, 1, 1, 1)
        self.SubDirLabel = QtGui.QLabel(WizardPage)
        self.SubDirLabel.setObjectName("SubDirLabel")
        self.gridLayout.addWidget(self.SubDirLabel, 2, 0, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "New package", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Enter a name for the new package. You can also enter a title and a description (optional but recommended).", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Package name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "Git URL or local path:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Title:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Description:", None, QtGui.QApplication.UnicodeUTF8))
        self.SubDirLabel.setText(QtGui.QApplication.translate("WizardPage", "git sub dir (optional git)", None, QtGui.QApplication.UnicodeUTF8))

