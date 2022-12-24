# Class for my window to import a list

import logging

from PySide6 import QtWidgets

import graphique.ImportListWindow

class ImportList(QtWidgets.QWidget, graphique.ImportListWindow.Ui_ImportListWindow):

    def __init__(self, window_instance):
        """
        Classe qui affiche une fenêtre pour pouvoir y coller une liste à rechercher
        :param window_instance: Une instance de la fenêtre principale
        """
        self.window_instance = window_instance
        super(ImportList, self).__init__()
        self.setupUi(self)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        # Setup of connections between widgets and other functions
        self.pushButton.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.import_list)

    def import_list(self):
        #self.window_instance.lineEdit.setText("")
        self.close()
        #self.window_instance.textEdit.setText("Recherche en cours...")
        #QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
        servers_textedit_list = self.textEdit.toPlainText()
        if servers_textedit_list:  # If the list of servers entered is not empty (if there are things in the textedit)
            servers_textedit_list = [y for y in (server_textedit_list.strip() for server_textedit_list in servers_textedit_list.splitlines()) if y]  # List comprehension: Create a Python list from the list entered in the textedit box
            #self.tools_instance.search(servers_textedit_list)  # TPO A MODIFIER !!!
            servers_textedit_string = ' '.join(servers_textedit_list)
            self.window_instance.lineEdit.setText(servers_textedit_string)
            self.window_instance.textEdit.setText("Vous pouvez maintenant lancer la recherche en cliquant sur l'icone de recherche ou en appuyant sur la touche entrée.")
        else:
            self.window_instance.textEdit.setText("La recherche n'a pas été faite car la liste fournie était vide.")
            logging.debug(f"Rien n'a été entré dans la barre de recherche")
            self.window_instance.lineEdit.setText("")  # On vide la barre de recherche
            self.window_instance.tableView.setModel(None)  # On vide le tableview (en retirant le model qui lui est appliqué)
