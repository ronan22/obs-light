# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProject.ui'
#
# Created: Tue Dec 20 09:23:03 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.8
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPageWrapper):
        WizardPageWrapper.setObjectName("WizardPageWrapper")
        WizardPageWrapper.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(WizardPageWrapper)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtGui.QListWidget(WizardPageWrapper)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)

        self.retranslateUi(WizardPageWrapper)
        QtCore.QMetaObject.connectSlotsByName(WizardPageWrapper)

    def retranslateUi(self, WizardPageWrapper):
        WizardPageWrapper.setWindowTitle(QtGui.QApplication.translate("WizardPageWrapper", "WizardPageWrapper", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setTitle(QtGui.QApplication.translate("WizardPageWrapper", "Project selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPageWrapper.setSubTitle(QtGui.QApplication.translate("WizardPageWrapper", "Select a project to import.", None, QtGui.QApplication.UnicodeUTF8))

