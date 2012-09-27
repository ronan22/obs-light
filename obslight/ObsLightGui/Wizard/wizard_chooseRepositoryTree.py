# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseRepositoryTree.ui'
#
# Created: Thu Sep 27 16:48:53 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(449, 304)
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.repositoryTreeView = QtGui.QTreeView(WizardPage)
        self.repositoryTreeView.setObjectName("repositoryTreeView")
        self.gridLayout.addWidget(self.repositoryTreeView, 0, 0, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Select repository template", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Select a repository template", None, QtGui.QApplication.UnicodeUTF8))

