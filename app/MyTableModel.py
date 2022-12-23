import csv
import io
import operator

from PySide6 import QtGui, QtCore, QtWidgets


# Class for tableview

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, mylist, header, parent=None, *args, window_instance):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.window_instance = window_instance
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent=None, *unused1, **unused2):
        return len(self.mylist)

    def columnCount(self, parent=None, *unused1, **unused2):
        return len(self.mylist[0])

    # def flags(self, index):
    #     return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def data(self, index, role=None):

        data = self.mylist[index.row()][index.column()]

        if not index.isValid():
            return None

        if role == QtCore.Qt.BackgroundRole and data == "Non présent dans les exports":
            #  if role == QtCore.Qt.BackgroundRole and (data == "VM Name not in RVTools or OPCA exports." or data == "DNS Name or TAGS not in RVTools or OPCA exports."):
            return QtGui.QColor("orange")  # return QBrush(QtCore.Qt.red) # fonctionne aussi

        # if role == QtCore.Qt.BackgroundRole and data == "0":
        #     return QtGui.QColor("orange")  # return QBrush(QtCore.Qt.orange) # fonctionne aussi

        elif role != QtCore.Qt.DisplayRole:
            return None
        return data

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order=None):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist, key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    # add event filter sur la détection des touches CTRL+C
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and event.matches(QtGui.QKeySequence.Copy):
            # print("CTRL+C detected")
            selection = self.window_instance.tableView.selectedIndexes()
            # print(selection) # ---> Si je sélectionne la première colonne (0) deuxième ligne (1) => [<PySide2.QtCore.QModelIndex(0,1,0x0,MyTableModel(0xbca0e90))  at 0x0000000009F1BD08>]
            if selection:
                rows = sorted(index.row() for index in selection)
                columns = sorted(index.column() for index in selection)
                rowcount = rows[-1] - rows[0] + 1
                colcount = columns[-1] - columns[0] + 1
                table = [[''] * colcount for _ in range(rowcount)]
                for index in selection:
                    row = index.row() - rows[0]
                    column = index.column() - columns[0]
                    table[row][column] = index.data()
                stream = io.StringIO()
                csv.writer(stream, delimiter=';').writerows(table)  # Si on ne précise pas le delimiter, on aura des ","
                QtWidgets.QApplication.clipboard().setText(stream.getvalue())
            return True
        return super(QtCore.QAbstractTableModel, self).eventFilter(source, event)
