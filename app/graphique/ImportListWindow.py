# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'H:\data\users\tpo\Tools\GITLAB\finder\app\graphique\ImportListWindow.ui',
# licensing of 'H:\data\users\tpo\Tools\GITLAB\finder\app\graphique\ImportListWindow.ui' applies.
#
# Created: Thu Aug 19 18:39:21 2021
#      by: pyside2-uic  running on PySide2 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore, QtGui, QtWidgets

class Ui_ImportListWindow(object):
    def setupUi(self, ImportListWindow):
        ImportListWindow.setObjectName("ImportListWindow")
        ImportListWindow.resize(397, 522)
        self.gridLayout = QtWidgets.QGridLayout(ImportListWindow)
        self.gridLayout.setObjectName("gridLayout")
        self.textEdit = QtWidgets.QTextEdit(ImportListWindow)
        self.textEdit.setPlaceholderText("")
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 0, 0, 1, 2)
        self.pushButton = QtWidgets.QPushButton(ImportListWindow)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(ImportListWindow)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)

        self.retranslateUi(ImportListWindow)
        QtCore.QMetaObject.connectSlotsByName(ImportListWindow)

    def retranslateUi(self, ImportListWindow):
        ImportListWindow.setWindowTitle(QtWidgets.QApplication.translate("ImportListWindow", "Entrer une liste à rechercher", None, -1))
        self.pushButton.setText(QtWidgets.QApplication.translate("ImportListWindow", "Cancel", None, -1))
        self.pushButton_2.setText(QtWidgets.QApplication.translate("ImportListWindow", "Search", None, -1))

