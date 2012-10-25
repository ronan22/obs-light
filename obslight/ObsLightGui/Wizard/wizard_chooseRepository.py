# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseRepository.ui'
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
        self.DelRepositoryButton = QtGui.QPushButton(WizardPage)
        self.DelRepositoryButton.setObjectName("DelRepositoryButton")
        self.gridLayout.addWidget(self.DelRepositoryButton, 7, 2, 1, 1)
        self.RepoTableView = QtGui.QTableView(WizardPage)
        self.RepoTableView.setEnabled(False)
        self.RepoTableView.setObjectName("RepoTableView")
        self.gridLayout.addWidget(self.RepoTableView, 4, 0, 1, 3)
        self.repositoryNameEdit = QtGui.QLineEdit(WizardPage)
        self.repositoryNameEdit.setObjectName("repositoryNameEdit")
        self.gridLayout.addWidget(self.repositoryNameEdit, 6, 0, 1, 1)
        self.repositoryUrlEdit = QtGui.QLineEdit(WizardPage)
        self.repositoryUrlEdit.setObjectName("repositoryUrlEdit")
        self.gridLayout.addWidget(self.repositoryUrlEdit, 6, 1, 1, 1)
        self.label = QtGui.QLabel(WizardPage)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 5, 1, 1, 1)
        self.AddRepositoryButton = QtGui.QPushButton(WizardPage)
        self.AddRepositoryButton.setObjectName("AddRepositoryButton")
        self.gridLayout.addWidget(self.AddRepositoryButton, 6, 2, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Repository configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Build against repo\'s URL", None, QtGui.QApplication.UnicodeUTF8))
        self.DelRepositoryButton.setText(QtGui.QApplication.translate("WizardPage", "Del Repo", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Repository Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Repository URL", None, QtGui.QApplication.UnicodeUTF8))
        self.AddRepositoryButton.setText(QtGui.QApplication.translate("WizardPage", "Add Repo", None, QtGui.QApplication.UnicodeUTF8))

