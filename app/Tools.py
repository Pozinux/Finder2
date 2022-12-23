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

    finished = QtCore.Signal()  # Signal pour fin du Thread
    searched_string_signal = QtCore.Signal(object)  # On créé un signal pour envoyer le mot cherché en cours vers la fenêtre principale
    signal_results_query_search = QtCore.Signal(object)  # On créé un signal pour envoyer le résultat de la recherche vers la fenêtre principale
    signal_textEdit_setText = QtCore.Signal(object)  # On créé un signal pour envoyer une string vers la fenêtre principale
    signal_display_warning_box = QtCore.Signal(object, object)  # On créé un signal pour envoyer un titre et un texte pour une popup warning vers la fenêtre principale
    

    def __init__(self):
        super().__init__()
        

    def is_db_empty(self):
        with DatabaseGestionSqlite.DatabaseGestionSqlite() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                message = "Vérification en cours que la base de données n'est pas vide..."
                logging.debug(message)
                self.signal_textEdit_setText.emit(message)

                db_connection.sql_query_execute(f'SELECT * FROM serveur_vmware')
                if db_connection.error_db_execution is None:
                    rows_vmware = db_connection.cursor.fetchall()
                    if not rows_vmware:
                        logging.debug("Base VMware vide ! Importer un export par Fichier > Importer un export...")
                        self.signal_textEdit_setText.emit("Base VMware vide !\n\nImporter un export en cliquant sur 'Fichier' puis 'Importer un export...'")
                        return True
                    else:
                       logging.debug("Base VMware non-vide.") 
                else:
                    #TPO#self.window_instance.textEdit.setText("Erreur lors de l'exécution des requêtes (Sélectionner les lignes VMware) sur la base de données.")
                    logging.debug(db_connection.error_db_execution)
                
                db_connection.sql_query_execute(f'SELECT * FROM serveur_opca')
                if db_connection.error_db_execution is None:
                    rows_opca = db_connection.cursor.fetchall()
                    if not rows_opca:
                        logging.debug("Base OPCA vide ! Importer un export par Fichier > Importer un export...")
                        self.signal_textEdit_setText.emit("Base OPCA vide !\n\nImporter un export en cliquant sur 'Fichier' puis 'Importer un export...'")
                        return True
                    else:
                       logging.debug("Base OPCA non-vide.") 
                else:
                    #TPO#self.window_instance.textEdit.setText("Erreur lors de l'exécution des requêtes (Sélectionner les lignes OPCA) sur la base de données.")
                    logging.debug(db_connection.error_db_execution)
            else:
                #TPO#self.window_instance.textEdit.setText("Erreur de connexion à la base de données.")
                logging.debug(db_connection.error_db_connection)

    def is_file_authorized(self, file):
        """ If the file is in the list of authorized_files, we copy the file
        :param file: Name of the file with its extension
        :return: A booleen True if the file is part of the authorized list or False if not
        """

        #TPO#if file in #TPO#self.window_instance.authorized_files_source_list:  # Lire l'attribut de l'instance qui a déjà été initialisé
       #TPO#     logging.debug(f"is_file_authorized : \"{file}\" is an authorized file.")
        #TPO#    file_authorized = True
       #TPO# else:
      #TPO#      logging.debug(f"is_file_authorized : \"{file}\" is not an authorized file.")
       #TPO#     file_authorized = False

      #TPO#  return file_authorized
        return True

    # def list_exports(self, export_type):
    #     # Check if there are any exports in the folder concerned
    #     if not os.listdir(fr"{constantes.EXPORTS_DIR}\exports_{export_type}"):
    #         #TPO#self.window_instance.textEdit.setText(f"Le répertoire des exports exports_{export_type} est vide.")
    #     else:
    #         # Creates a list of files that are in the export folder where each element is of the type 'C:\\path\file.ext'
    #         files_paths_list = []
    #         exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
    #         for root, dirs, files in os.walk(exports_files_folder_path):
    #             for file in files:
    #                 files_paths_list.append(os.path.join(root, file))
    #         number_authorized = number_not_authorized = 0
    #         files_authorized_list = []
    #         files_not_authorized_list = []
    #         for file_path in files_paths_list:
    #             file = os.path.basename(file_path)
    #             file_is_authorized = self.is_file_authorized(file)
    #             if file_is_authorized:
    #                 number_authorized += 1
    #                 files_authorized_list.append(file)
    #             else:
    #                 number_not_authorized += 1
    #                 files_not_authorized_list.append(file)
                
    #         #files_not_authorized_list.remove('.gitkeep')  # Ne pas afficher les fichiers .gitkeep comme des fichiers non-autorisés /!\ Créé une erreur si le fichier n'existe pas

    #         if files_authorized_list:
    #             list_result_cr_authorized = "\n".join(files_authorized_list)
    #             result_search_authorized = f"Nombre de fichiers autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_authorized)}\n\n{list_result_cr_authorized}"
    #         else:
    #             result_search_authorized = "Pas de fichiers autorisés trouvés dans le répertoire des exports."

    #         if files_not_authorized_list:
    #             list_result_cr_not_authorized = "\n".join(files_not_authorized_list)
    #             result_search_not_authorized = f"Nombre de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type} : {str(number_not_authorized)}\n\n{list_result_cr_not_authorized}"
    #         else:
    #             result_search_not_authorized = f"Pas de fichiers non-autorisés trouvés dans le répertoire des exports export_{export_type}."

    #         #TPO#self.window_instance.textEdit.setText(f"{result_search_authorized}\n\n{result_search_not_authorized}")