# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ols.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(480, 320)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 290, 461, 21))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.queryLine = QtWidgets.QLineEdit(Dialog)
        self.queryLine.setGeometry(QtCore.QRect(10, 20, 421, 25))
        self.queryLine.setInputMethodHints(QtCore.Qt.ImhLatinOnly)
        self.queryLine.setClearButtonEnabled(False)
        self.queryLine.setObjectName("queryLine")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 5, 64, 15))
        self.label.setObjectName("label")
        self.searchButton = QtWidgets.QPushButton(Dialog)
        self.searchButton.setGeometry(QtCore.QRect(440, 20, 31, 26))
        self.searchButton.setStyleSheet("font: 14pt url(:/fonts/assets/fonts/EBI-Functional.ttf);\n"
"font-family: \"EBI-Functional\";")
        self.searchButton.setDefault(True)
        self.searchButton.setObjectName("searchButton")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(200, 120, 271, 161))
        self.textEdit.setObjectName("textEdit")
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(230, 50, 241, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(230, 80, 241, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.ontoTree = QtWidgets.QTreeView(Dialog)
        self.ontoTree.setGeometry(QtCore.QRect(10, 50, 181, 231))
        self.ontoTree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ontoTree.setAutoExpandDelay(0)
        self.ontoTree.setObjectName("ontoTree")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Query"))
        self.searchButton.setText(_translate("Dialog", "1"))

import resources_rc
