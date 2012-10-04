# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseManifest.ui'
#
# Created: Wed Oct  3 19:10:29 2012
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
        self.gridLayout.addWidget(self.listManifestButton, 4, 1, 1, 1)
        self.ManifestListWidget = QtGui.QListWidget(WizardPage)
        self.ManifestListWidget.setObjectName("ManifestListWidget")
        self.gridLayout.addWidget(self.ManifestListWidget, 5, 1, 1, 2)
        self.liveManifestButton = QtGui.QRadioButton(WizardPage)
        self.liveManifestButton.setObjectName("liveManifestButton")
        self.gridLayout.addWidget(self.liveManifestButton, 6, 1, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Select manifest.", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "manifest contains Git repositories for the Repo source code (standard Android manifest files.)", None, QtGui.QApplication.UnicodeUTF8))
        self.listManifestButton.setText(QtGui.QApplication.translate("WizardPage", "List of OBS Light manifest", None, QtGui.QApplication.UnicodeUTF8))
        self.liveManifestButton.setText(QtGui.QApplication.translate("WizardPage", "Tizen Live manifest", None, QtGui.QApplication.UnicodeUTF8))

