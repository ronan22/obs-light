# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProject.ui'
#
# Created: Tue Dec 18 10:43:52 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(430, 338)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.filterLineEdit = QtGui.QLineEdit(WizardPage)
        self.filterLineEdit.setObjectName("filterLineEdit")
        self.gridLayout.addWidget(self.filterLineEdit, 0, 1, 1, 1)
        self.projectListWidget = QtGui.QListWidget(WizardPage)
        self.projectListWidget.setObjectName("projectListWidget")
        self.gridLayout.addWidget(self.projectListWidget, 1, 0, 1, 2)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 1, 1, 1)
        self.restrainRemoteLinksCheckBox = QtGui.QCheckBox(WizardPage)
        self.restrainRemoteLinksCheckBox.setObjectName("restrainRemoteLinksCheckBox")
        self.gridLayout.addWidget(self.restrainRemoteLinksCheckBox, 3, 1, 1, 1)
        self.restrainMaintainerCheckBox = QtGui.QCheckBox(WizardPage)
        self.restrainMaintainerCheckBox.setEnabled(True)
        self.restrainMaintainerCheckBox.setChecked(False)
        self.restrainMaintainerCheckBox.setObjectName("restrainMaintainerCheckBox")
        self.gridLayout.addWidget(self.restrainMaintainerCheckBox, 4, 1, 1, 1)
        self.restrainBugownerCheckBox = QtGui.QCheckBox(WizardPage)
        self.restrainBugownerCheckBox.setObjectName("restrainBugownerCheckBox")
        self.gridLayout.addWidget(self.restrainBugownerCheckBox, 5, 1, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Project selection", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Select a project to import.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Filter:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Warrnig These options can increase the response time substantially.", None, QtGui.QApplication.UnicodeUTF8))
        self.restrainRemoteLinksCheckBox.setText(QtGui.QApplication.translate("WizardPage", "Show only projects which are remote links", None, QtGui.QApplication.UnicodeUTF8))
        self.restrainMaintainerCheckBox.setText(QtGui.QApplication.translate("WizardPage", "Show only projects on which I am maintainer", None, QtGui.QApplication.UnicodeUTF8))
        self.restrainBugownerCheckBox.setText(QtGui.QApplication.translate("WizardPage", "Show only projects on which I am bugowner", None, QtGui.QApplication.UnicodeUTF8))

