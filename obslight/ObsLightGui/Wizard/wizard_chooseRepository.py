# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseRepository.ui'
#
# Created: Thu Sep 20 16:01:36 2012
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
        self.RepoListWidget = QtGui.QListWidget(WizardPage)
        self.RepoListWidget.setEnabled(False)
        self.RepoListWidget.setObjectName("RepoListWidget")
        self.gridLayout.addWidget(self.RepoListWidget, 3, 0, 1, 2)
        self.AddRepositoryButton = QtGui.QPushButton(WizardPage)
        self.AddRepositoryButton.setObjectName("AddRepositoryButton")
        self.gridLayout.addWidget(self.AddRepositoryButton, 1, 1, 1, 1)
        self.lineEdit = QtGui.QLineEdit(WizardPage)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.autoAddRepoButton = QtGui.QCheckBox(WizardPage)
        self.autoAddRepoButton.setEnabled(True)
        self.autoAddRepoButton.setChecked(True)
        self.autoAddRepoButton.setObjectName("autoAddRepoButton")
        self.gridLayout.addWidget(self.autoAddRepoButton, 4, 0, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Repository configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Build against repo\'s URL", None, QtGui.QApplication.UnicodeUTF8))
        self.AddRepositoryButton.setText(QtGui.QApplication.translate("WizardPage", "Add URL", None, QtGui.QApplication.UnicodeUTF8))
        self.autoAddRepoButton.setText(QtGui.QApplication.translate("WizardPage", "Add repository of the project.", None, QtGui.QApplication.UnicodeUTF8))

