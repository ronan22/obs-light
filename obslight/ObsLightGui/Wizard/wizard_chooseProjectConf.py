# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_chooseProjectConf.ui'
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
        self.LocalConfListWidget = QtGui.QListWidget(WizardPage)
        self.LocalConfListWidget.setEnabled(False)
        self.LocalConfListWidget.setObjectName("LocalConfListWidget")
        self.gridLayout.addWidget(self.LocalConfListWidget, 4, 1, 1, 2)
        self.chooseConfButton = QtGui.QRadioButton(WizardPage)
        self.chooseConfButton.setObjectName("chooseConfButton")
        self.gridLayout.addWidget(self.chooseConfButton, 3, 1, 1, 1)
        self.LocalGbsConfListWidget = QtGui.QListWidget(WizardPage)
        self.LocalGbsConfListWidget.setObjectName("LocalGbsConfListWidget")
        self.gridLayout.addWidget(self.LocalGbsConfListWidget, 8, 1, 1, 2)
        self.LoadConfFileButton = QtGui.QPushButton(WizardPage)
        self.LoadConfFileButton.setObjectName("LoadConfFileButton")
        self.gridLayout.addWidget(self.LoadConfFileButton, 10, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(WizardPage)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 10, 1, 1, 1)
        self.chooseGbsConfButton = QtGui.QRadioButton(WizardPage)
        self.chooseGbsConfButton.setObjectName("chooseGbsConfButton")
        self.gridLayout.addWidget(self.chooseGbsConfButton, 5, 1, 1, 1)
        self.addNewConfButton = QtGui.QRadioButton(WizardPage)
        self.addNewConfButton.setChecked(True)
        self.addNewConfButton.setObjectName("addNewConfButton")
        self.gridLayout.addWidget(self.addNewConfButton, 9, 1, 1, 1)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "File configure configuration", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "The project conf denotes the (build) configuration of a project. http://en.opensuse.org/openSUSE:Build_Service_prjconf#Description", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseConfButton.setText(QtGui.QApplication.translate("WizardPage", "Choose conf from OBS Light list:", None, QtGui.QApplication.UnicodeUTF8))
        self.LoadConfFileButton.setText(QtGui.QApplication.translate("WizardPage", "Load File", None, QtGui.QApplication.UnicodeUTF8))
        self.chooseGbsConfButton.setText(QtGui.QApplication.translate("WizardPage", "Choose conf from gbs list:", None, QtGui.QApplication.UnicodeUTF8))
        self.addNewConfButton.setText(QtGui.QApplication.translate("WizardPage", "New conf file", None, QtGui.QApplication.UnicodeUTF8))

