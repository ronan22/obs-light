# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseNewOrExistingProject.ui'
#
# Created: Wed May 16 09:56:48 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtGui.QVBoxLayout(WizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.chooseExistingProjectButton = QtGui.QRadioButton(WizardPage)
        self.chooseExistingProjectButton.setChecked(True)
        self.chooseExistingProjectButton.setObjectName("chooseExistingProjectButton")
        self.verticalLayout.addWidget(self.chooseExistingProjectButton)
        self.createNewProjectButton = QtGui.QRadioButton(WizardPage)
        self.createNewProjectButton.setObjectName("createNewProjectButton")
        self.verticalLayout.addWidget(self.createNewProjectButton)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Existing project or new project ?", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "You can either select a project already existing on server, or create a new project. Non-admin users can only create subprojects of their home project.", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseExistingProjectButton.setText(QtGui.QApplication.translate("WizardPage", "Select an existing project", None, QtGui.QApplication.UnicodeUTF8))
        self.createNewProjectButton.setText(QtGui.QApplication.translate("WizardPage", "Create a new project", None, QtGui.QApplication.UnicodeUTF8))

