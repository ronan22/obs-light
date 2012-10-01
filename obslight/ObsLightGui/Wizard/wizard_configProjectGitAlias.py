# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/wizard_configProjectGitAlias.ui'
#
# Created: Thu Sep 27 18:18:50 2012
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
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtGui.QLabel(WizardPage)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.architectureLabel = QtGui.QLabel(WizardPage)
        self.architectureLabel.setObjectName("architectureLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.architectureLabel)
        self.label_4 = QtGui.QLabel(WizardPage)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_4)
        self.aliasLineEdit = QtGui.QLineEdit(WizardPage)
        self.aliasLineEdit.setObjectName("aliasLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.aliasLineEdit)
        self.label_6 = QtGui.QLabel(WizardPage)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.label_6)
        self.label_5 = QtGui.QLabel(WizardPage)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_5)
        self.createGbsChrootCheckBox = QtGui.QCheckBox(WizardPage)
        self.createGbsChrootCheckBox.setText("")
        self.createGbsChrootCheckBox.setObjectName("createGbsChrootCheckBox")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.createGbsChrootCheckBox)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        WizardPage.setWindowTitle(QtGui.QApplication.translate("WizardPage", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setTitle(QtGui.QApplication.translate("WizardPage", "Choose project alias", None, QtGui.QApplication.UnicodeUTF8))
        WizardPage.setSubTitle(QtGui.QApplication.translate("WizardPage", "Choose an alias for the project, and choose to create a chroot jail now (can be done later).", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("WizardPage", "Architecture:", None, QtGui.QApplication.UnicodeUTF8))
        self.architectureLabel.setText(QtGui.QApplication.translate("WizardPage", "architecture", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("WizardPage", "Alias:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("WizardPage", "Green --> OK\n"
"Red --> Already in use", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("WizardPage", "Create chroot jail:", None, QtGui.QApplication.UnicodeUTF8))

