# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseLocalGbsOrOBSProject.ui'
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
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WizardPage.sizePolicy().hasHeightForWidth())
        WizardPage.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.LocalProjectRadioButton = QtGui.QRadioButton(WizardPage)
        self.LocalProjectRadioButton.setObjectName("LocalProjectRadioButton")
        self.gridLayout.addWidget(self.LocalProjectRadioButton, 0, 1, 1, 1)
        self.radioButton_2 = QtGui.QRadioButton(WizardPage)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout.addWidget(self.radioButton_2, 1, 1, 1, 1)
        self.label = QtGui.QLabel(WizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 2, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Choose project type.", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "choose between OBS project or local project  (gbs like).", None, QtGui.QApplication.UnicodeUTF8))
        self.LocalProjectRadioButton.setText(QtGui.QApplication.translate("WizardPage", "Local  Project", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButton_2.setText(QtGui.QApplication.translate("WizardPage", "OBS Server Project", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "Choose the Project Type", None, QtGui.QApplication.UnicodeUTF8))

