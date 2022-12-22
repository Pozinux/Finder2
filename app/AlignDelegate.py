from PySide6 import QtWidgets, QtCore


# Class for tableview pour aligner le texte dans les colonnes du tableau
# noinspection PyArgumentList


class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter
