# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProjectTemplate.ui'
#
# Created: Thu Oct  4 14:14:54 2012
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
        self.chooseObslightDefaultButton = QtGui.QRadioButton(WizardPage)
        self.chooseObslightDefaultButton.setChecked(True)
        self.chooseObslightDefaultButton.setObjectName("chooseObslightDefaultButton")
        self.gridLayout.addWidget(self.chooseObslightDefaultButton, 0, 0, 1, 1)
        self.chooseNewLocalProjectButton = QtGui.QRadioButton(WizardPage)
        self.chooseNewLocalProjectButton.setObjectName("chooseNewLocalProjectButton")
        self.gridLayout.addWidget(self.chooseNewLocalProjectButton, 1, 0, 1, 2)
        self.LocalProjectListWidget = QtGui.QListWidget(WizardPage)
        self.LocalProjectListWidget.setEnabled(False)
        self.LocalProjectListWidget.setObjectName("LocalProjectListWidget")
        self.gridLayout.addWidget(self.LocalProjectListWidget, 2, 0, 1, 2)
        self.projectTemplateConfLabel = QtGui.QLabel(WizardPage)
        self.projectTemplateConfLabel.setText("")
        self.projectTemplateConfLabel.setObjectName("projectTemplateConfLabel")
        self.gridLayout.addWidget(self.projectTemplateConfLabel, 0, 1, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QObject.connect(self.chooseNewLocalProjectButton, QtCore.SIGNAL("toggled(bool)"), self.LocalProjectListWidget.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Local Project configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "You can configure a new local project or choose on from a template list.", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseObslightDefaultButton.setText(QtGui.QApplication.translate("WizardPage", "Default OBS Light gbs project Conf:", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseNewLocalProjectButton.setText(QtGui.QApplication.translate("WizardPage", "Choose gbs Project from template list:", None, QtGui.QApplication.UnicodeUTF8))

