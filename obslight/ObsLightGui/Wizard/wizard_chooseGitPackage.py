# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseGitPackage.ui'
#
# Created: Mon Oct 22 16:44:50 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.gitProjectTreeView = QtGui.QTreeView(WizardPage)
        self.gitProjectTreeView.setObjectName("gitProjectTreeView")
        self.gridLayout.addWidget(self.gitProjectTreeView, 0, 0, 1, 3)
        self.selectAllPushButton = QtGui.QPushButton(WizardPage)
        self.selectAllPushButton.setObjectName("selectAllPushButton")
        self.gridLayout.addWidget(self.selectAllPushButton, 1, 0, 1, 1)
        self.unselectAllPushButton = QtGui.QPushButton(WizardPage)
        self.unselectAllPushButton.setObjectName("unselectAllPushButton")
        self.gridLayout.addWidget(self.unselectAllPushButton, 1, 1, 1, 1)
        self.CheckUserNameButton = QtGui.QPushButton(WizardPage)
        self.CheckUserNameButton.setToolTip("")
        self.CheckUserNameButton.setObjectName("CheckUserNameButton")
        self.gridLayout.addWidget(self.CheckUserNameButton, 3, 0, 1, 1)
        self.userTizenGitNameLineEdit = QtGui.QLineEdit(WizardPage)
        self.userTizenGitNameLineEdit.setObjectName("userTizenGitNameLineEdit")
        self.gridLayout.addWidget(self.userTizenGitNameLineEdit, 3, 1, 1, 2)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllPushButton.setText(QtGui.QApplication.translate("WizardPage", "Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.unselectAllPushButton.setText(QtGui.QApplication.translate("WizardPage", "Deselect All", None, QtGui.QApplication.UnicodeUTF8))
        self.CheckUserNameButton.setText(QtGui.QApplication.translate("WizardPage", "Check User Name", None, QtGui.QApplication.UnicodeUTF8))
        self.userTizenGitNameLineEdit.setToolTip(QtGui.QApplication.translate("WizardPage", "Enter your Tizen Git login name.", None, QtGui.QApplication.UnicodeUTF8))

