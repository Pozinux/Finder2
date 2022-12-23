import logging
import os
import time

from PySide6 import QtCore

import AlignDelegate
import DatabaseGestionSqlite
import MyTableModel
import constantes

# Les fonctions dans Tools ont besoin de l'UI. Donc je passe une instance de l'UI.

#class Tools(QtWidgets.QWidget, QtCore.QObject):
class Tools(QtCore.QObject):

    def __init__(self):
        super().__init__()


    def is_file_authorized(self, file):
        """ If the file is in the list of authorized_files, we copy the file
        :param file: Name of the file with its extension
        :return: A booleen True if the file is part of the authorized list or False if not
        """

        if file in self.window_instance.authorized_files_source_list:  # Lire l'attribut de l'instance qui a déjà été initialisé
            logging.debug(f"is_file_authorized : \"{file}\" is an authorized file.")
            file_authorized = True
        else:
            logging.debug(f"is_file_authorized : \"{file}\" is not an authorized file.")
            file_authorized = False

        return file_authorized
        return True

    def list_exports(self, export_type):
        # Check if there are any exports in the folder concerned
        if not os.listdir(fr"{constantes.EXPORTS_DIR}\exports_{export_type}"):
            self.window_instance.textEdit.setText(f"Le répertoire des exports exports_{export_type} est vide.")
        else:
            # Creates a list of files that are in the export folder where each element is of the type 'C:\\path\file.ext'
            files_paths_list = []
            exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
            for root, dirs, files in os.walk(exports_files_folder_path):
                for file in files:
                    files_paths_list.append(os.path.join(root, file))
            number_authorized = number_not_authorized = 0
            files_authorized_list = []
            files_not_authorized_list = []
            for file_path in files_paths_list:
                file = os.path.basename(file_path)
                file_is_authorized = self.is_file_authorized(file)
                if file_is_authorized:
                    number_authorized += 1
                    files_authorized_list.append(file)
                else:
                    number_not_authorized += 1
                    files_not_authorized_list.append(file)
                
            files_not_authorized_list.remove('.gitkeep')  # Ne pas afficher les fichiers .gitkeep comme des fichiers non-autorisés /!\ Créé une erreur si le fichier n'existe pas

            if files_authorized_list:
                list_result_cr_authorized = "\n".join(files_authorized_list)
                result_search_authorized = f"Nombre de fichiers autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_authorized)}\n\n{list_result_cr_authorized}"
            else:
                result_search_authorized = "Pas de fichiers autorisés trouvés dans le répertoire des exports."

            if files_not_authorized_list:
                list_result_cr_not_authorized = "\n".join(files_not_authorized_list)
                result_search_not_authorized = f"Nombre de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_not_authorized)}\n\n{list_result_cr_not_authorized}"
            else:
                result_search_not_authorized = f"Pas de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type}."

            self.window_instance.textEdit.setText(f"{result_search_authorized}\n\n{result_search_not_authorized}")