# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseManifest.ui'
#
# Created: Thu Sep 27 18:18:49 2012
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
        self.listManifestButton = QtGui.QRadioButton(WizardPage)
        self.listManifestButton.setChecked(True)
        self.listManifestButton.setObjectName("listManifestButton")
        self.gridLayout.addWidget(self.listManifestButton, 4, 0, 1, 1)
        self.ManifestListWidget = QtGui.QListWidget(WizardPage)
        self.ManifestListWidget.setObjectName("ManifestListWidget")
        self.gridLayout.addWidget(self.ManifestListWidget, 5, 0, 1, 2)
        self.customManifestButton = QtGui.QRadioButton(WizardPage)
        self.customManifestButton.setObjectName("customManifestButton")
        self.gridLayout.addWidget(self.customManifestButton, 7, 0, 1, 1)
        self.lineManifestEdit = QtGui.QLineEdit(WizardPage)
        self.lineManifestEdit.setObjectName("lineManifestEdit")
        self.gridLayout.addWidget(self.lineManifestEdit, 8, 0, 1, 1)
        self.loadManifestPushButton = QtGui.QPushButton(WizardPage)
        self.loadManifestPushButton.setObjectName("loadManifestPushButton")
        self.gridLayout.addWidget(self.loadManifestPushButton, 8, 1, 1, 1)
        self.liveManifestButton = QtGui.QRadioButton(WizardPage)
        self.liveManifestButton.setObjectName("liveManifestButton")
        self.gridLayout.addWidget(self.liveManifestButton, 9, 0, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Select manifest.", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "manifest contains Git repositories for the Repo source code (standard Android manifest files.)", None, QtGui.QApplication.UnicodeUTF8))
        self.listManifestButton.setText(QtGui.QApplication.translate("WizardPage", "List of OBS Light manifest", None, QtGui.QApplication.UnicodeUTF8))
        self.customManifestButton.setText(QtGui.QApplication.translate("WizardPage", "Custom manifest", None, QtGui.QApplication.UnicodeUTF8))
        self.loadManifestPushButton.setText(QtGui.QApplication.translate("WizardPage", "Load File", None, QtGui.QApplication.UnicodeUTF8))
        self.liveManifestButton.setText(QtGui.QApplication.translate("WizardPage", "Tizen Live manifest", None, QtGui.QApplication.UnicodeUTF8))

