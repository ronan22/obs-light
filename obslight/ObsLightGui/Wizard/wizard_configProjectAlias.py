# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configProjectAlias.ui'
#
# Created: Thu Sep 27 16:48:53 2012
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        WizardPage.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.formLayout = QtGui.QFormLayout(WizardPage)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(WizardPage)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.projectLabel = QtGui.QLabel(WizardPage)
        self.projectLabel.setObjectName("projectLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.projectLabel)
        self.label_2 = QtGui.QLabel(WizardPage)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.targetLabel = QtGui.QLabel(WizardPage)
        self.targetLabel.setObjectName("targetLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.targetLabel)
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.architectureLabel = QtGui.QLabel(WizardPage)
        self.architectureLabel.setObjectName("architectureLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.architectureLabel)
        self.label_4 = QtGui.QLabel(WizardPage)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.aliasLineEdit = QtGui.QLineEdit(WizardPage)
        self.aliasLineEdit.setAcceptDrops(False)
        self.aliasLineEdit.setReadOnly(True)
        self.aliasLineEdit.setObjectName("aliasLineEdit")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.aliasLineEdit)
        self.createChrootCheckBox = QtGui.QCheckBox(WizardPage)
        self.createChrootCheckBox.setText("")
        self.createChrootCheckBox.setObjectName("createChrootCheckBox")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.createChrootCheckBox)
        self.label_5 = QtGui.QLabel(WizardPage)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.label_5)
        self.label_6 = QtGui.QLabel(WizardPage)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.label_6)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Choose project alias", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Choose an alias for the project, and choose to create a chroot jail now (can be done later).", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("WizardPage", "OBS project:", None, QtGui.QApplication.UnicodeUTF8))
        self.projectLabel.setText(QtGui.QApplication.translate("WizardPage", "project", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("WizardPage", "Target:", None, QtGui.QApplication.UnicodeUTF8))
        self.targetLabel.setText(QtGui.QApplication.translate("WizardPage", "target", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Architecture:", None, QtGui.QApplication.UnicodeUTF8))
        self.architectureLabel.setText(QtGui.QApplication.translate("WizardPage", "architecture", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "Alias:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("WizardPage", "Create chroot jail:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("WizardPage", "Green --> OK\n"
"Red --> Already in use", None, QtGui.QApplication.UnicodeUTF8))

