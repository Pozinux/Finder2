import configparser
import logging
import os.path
import pathlib
import shutil
import time

import pandas
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path

import constantes
from DatabaseGestionSqlite import DatabaseGestionSqlite
from ImportList import ImportList
from Search import Search
from graphique.MainWindow import Ui_MainWindow
import MyTableModel
import AlignDelegate


# Class main graphical window
class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window, self).__init__()

        # --- Récupérer les infos des listes des fichiers autorisés
        # Liste full de toutes les fichiers autorisés
        self.authorized_files_source_list = []
        self.authorized_files_opca_source_list = []
        self.authorized_files_cmdb_source_list = []
        self.authorized_files_vmware_source_list = []
        self.authorized_files_cmdb_all_source_list = []
        self.files_renamed = []
        self.files_not_renamed = []
        self.result_folder_vmware = ""
        self.result_folder_opca = ""
        self.result_folder_cmdb = ""
        self.result_folder_cmdb_all = ""
        self.exports_folders_dates = ""

        # When opening the application, we create the database dans its tables in case they don't already exist
        self.create_database_and_tables()

        # Initialiser l'interface graphique
        self.setupUi(self)
        # Put the focus of the mouse on the input text area
        self.lineEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.lineEdit.setFocus()
        self.lineEdit.setMaxLength(500000)  # By default, this property contains a value of 32767 donc si on cherche une liste plus longue il va tronquer
        self.showMaximized()  # Pour ouvrir au démarrage en taille max la fenetre principale

        self.setup_connections()  # Establish connections between widgets and functions
        self.setup_checkbox()  # Setup the checkbox status
        self.setup_keyboard_shortcuts()  # Establish connections between keys and functions
        self.reset_progressbar_statusbar()  # When the window is launched, set the progress bar + status bar text to
        # self.textEdit.hide()  # When the window is launched, hide the textedit
        self.setWindowIcon(QtGui.QIcon("icons/window.png"))  # Set the window icon (does not work directly in QT Designer)
        self.menu_bar()  # Create the menu bar
        self.show()  # Display  main window

        # Creation of export directories when opening the application if they do not already exist
        pathlib.Path(constantes.EXPORTS_OPCA_DIR).mkdir(parents=True, exist_ok=True)  # Creating the opca export folder if it does not already exist
        pathlib.Path(constantes.EXPORTS_VMWARE_DIR).mkdir(parents=True, exist_ok=True)  # Creating the rvtools export folder if it does not already exist
        pathlib.Path(constantes.EXPORTS_CMDB_DIR).mkdir(parents=True, exist_ok=True)  # Creating the cmdb export folder if it does not already exist
        pathlib.Path(constantes.EXPORTS_CMDB_ALL_DIR).mkdir(parents=True, exist_ok=True)  # Creating the cmdb_all export folder if it does not already exist

        config_authorized_files_ini = Path("config/config_authorized_files.ini")
        if config_authorized_files_ini.is_file():
            self.list_authorized_files()  # Génére la liste des fichiers authorisés à l'ouverture de l'appli afin de pouvoir lister les exports (dans paramètres)
        else:
            self.textEdit.setText(f"Veuillez créer un fichier config/config_authorized_files.ini")
            logging.debug("config/config_authorized_files.ini doesn't not exist.")

    def __str__(self):
        return f"Liste des fichiers authorisés : {self.authorized_files_source_list}"

    def menu_bar(self):
        # Menu File > exit
        exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)

        # Menu fichier > Refesh BDD VMware
        refresh_bdd_vmware = QtGui.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour VMware', self)
        refresh_bdd_vmware.setStatusTip("Update the database from the RVTools that are present in the exports folder")
        refresh_bdd_vmware.triggered.connect(lambda: self.update_db("vmware"))

        # Menu fichier > Refesh BDD OPCA
        refresh_bdd_opca = QtGui.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour OPCA', self)
        refresh_bdd_opca.setStatusTip("Update the database from the OPCA exports that are present in the exports folder")
        refresh_bdd_opca.triggered.connect(lambda: self.update_db("opca"))

        # Menu fichier > Refesh BDD CMDB
        refresh_bdd_cmdb = QtGui.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour CMDB APPLI', self)
        refresh_bdd_cmdb.setStatusTip("Update the database from the CMDB exports that are present in the exports folder")
        refresh_bdd_cmdb.triggered.connect(lambda: self.update_db("cmdb"))

        # Menu fichier > Refesh BDD CMDB ALL
        refresh_bdd_cmdb_all = QtGui.QAction(QtGui.QIcon('icons/refresh.png'), '&Mise à jour CMDB ALL', self)
        refresh_bdd_cmdb_all.setStatusTip("Update the database from the CMDB ALL exports that are present in the exports folder")
        refresh_bdd_cmdb_all.triggered.connect(lambda: self.update_db("cmdb_all"))

        # Menu file > Renommer les exports
        rename_export = QtGui.QAction(QtGui.QIcon('icons/rename.png'), '&Renommer les exports', self)
        rename_export.setStatusTip("Renommer les fichiers d'exports en fonctions des infos du config_authorized_files.ini")
        rename_export.triggered.connect(self.rename_exports)

        # Menu Parameters > List the RVTools export files present
        list_exports_action_vmware = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports RVTools présents', self)
        list_exports_action_vmware.setStatusTip("Lists the RVTools VMware export files (.xls/.xlsx) present in the folder")
        list_exports_action_vmware.triggered.connect(lambda: self.list_exports("vmware"))

        # Menu Parameters > List the OPCA export files present
        list_exports_action_opca = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports OPCA présents', self)
        list_exports_action_opca.setStatusTip("Lists the OPCA export files (.csv) present in the folder")
        list_exports_action_opca.triggered.connect(lambda: self.list_exports("opca"))

        # Menu Parameters > List the CMDB export files present
        list_exports_action_cmdb = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports CMDB présents', self)
        list_exports_action_cmdb.setStatusTip("Lists the CMDB export files (.csv) present in the folder")
        list_exports_action_cmdb.triggered.connect(lambda: self.list_exports("cmdb"))

        # Menu Parameters > List the CMDB ALL export files present
        list_exports_action_cmdb_all = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les exports CMDB ALL présents', self)
        list_exports_action_cmdb_all.setStatusTip("Lists the CMDB ALL export files (.csv) present in the folder")
        list_exports_action_cmdb_all.triggered.connect(lambda: self.list_exports("cmdb_all"))

        # Menu Parameters > List the export files authorized to be imported into the database
        list_files_authorized_action = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les fichiers autorisés', self)
        list_files_authorized_action.setStatusTip("Liste les exports autorisés à être importés dans la base en fonction des informations du fichier .ini")
        list_files_authorized_action.triggered.connect(self.display_list_authorized_files)

        # Menu Parameters > Date de dernières modifications des exports
        list_last_modifications_exports_action = QtGui.QAction(QtGui.QIcon('icons/list.png'), '&Lister les dates de dernières modifications des exports', self)
        list_last_modifications_exports_action.setStatusTip("Liste les dates de dernieres modifications des exports")
        list_last_modifications_exports_action.triggered.connect(self.display_list_last_modifications_exports)

        # Menu About > About
        see_about_action = QtGui.QAction(QtGui.QIcon('icons/about.png'), '&A propos', self)
        see_about_action.setStatusTip("About")
        see_about_action.triggered.connect(self.see_about)

        self.menuFile.addAction(refresh_bdd_vmware)
        self.menuFile.addAction(refresh_bdd_opca)
        self.menuFile.addAction(refresh_bdd_cmdb)
        self.menuFile.addAction(refresh_bdd_cmdb_all)
        self.menuFile.addAction(rename_export)
        self.menuFile.addAction(exit_action)
        self.menuParameters.addAction(list_exports_action_vmware)
        self.menuParameters.addAction(list_exports_action_opca)
        self.menuParameters.addAction(list_exports_action_cmdb)
        self.menuParameters.addAction(list_exports_action_cmdb_all)
        self.menuParameters.addAction(list_files_authorized_action)
        self.menuParameters.addAction(list_last_modifications_exports_action)
        self.menuAbout.addAction(see_about_action)

    def rename_exports(self):
        self.files_renamed = []
        self.rename_imported_files_to_authorized_files("authorized_files_vmware", "vmware")
        self.rename_imported_files_to_authorized_files("authorized_files_opca", "opca")
        self.rename_imported_files_to_authorized_files("authorized_files_cmdb", "cmdb")
        self.rename_imported_files_to_authorized_files("authorized_files_cmdb_all", "cmdb_all")

    def rename_imported_files_to_authorized_files(self, section_ini_authorized_files, export_type):
        authorized_files_parser = configparser.ConfigParser()
        authorized_files_parser.read(constantes.CONFIG_AUTHORIZED_FILES_INI)
        dict_authorized_files = {}  # Init d'un dico des fichiers autorisés

        if authorized_files_parser.has_section(section_ini_authorized_files):
            authorized_files_items = authorized_files_parser.items(section_ini_authorized_files)
            for authorized_files_item in authorized_files_items:
                dict_authorized_files[authorized_files_item[0]] = authorized_files_item[1]
        else:
            raise Exception(f'Section {section_ini_authorized_files} not found in the {constantes.CONFIG_AUTHORIZED_FILES_INI} file.')

        for file in dict_authorized_files.items():
            try:
                os.rename(fr'exports\exports_{export_type}\\' + file[0], fr'exports\exports_{export_type}\\' + file[1])
                self.files_renamed.append(file[0])
            except FileNotFoundError:
                # print(file[0] + " : Ce fichier n'a pas été trouvé dans les exports présents.") # A décommenter pour le debug
                # self.files_not_renamed.append(file[0])
                pass

        if self.files_renamed:
            files_renamed_cr = "\n".join(self.files_renamed)
            self.textEdit.setText(f"Fichiers qui ont été renommés par l'opération :\n\n{files_renamed_cr}")
        else:
            self.textEdit.setText("Pas de fichiers à renommer trouvés dans le répertoire des exports.")

    def get_export_folder_date(self, export_type):

        last_modified_date = time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(fr"{constantes.EXPORTS_DIR}\exports_{export_type}")))

        if export_type == "vmware":
            self.result_folder_vmware = f"Exports {export_type} : {str(last_modified_date)}"
        elif export_type == "opca":
            self.result_folder_opca = f"Exports {export_type} : {str(last_modified_date)}"
        elif export_type == "cmdb":
            self.result_folder_cmdb = f"Exports {export_type} : {str(last_modified_date)}"
        elif export_type == "cmdb_all":
            self.result_folder_cmdb_all = f"Exports {export_type} : {str(last_modified_date)}"

    @staticmethod
    def read_authorized_files_config(section_ini_authorized_files):
        # Create a dictionary of authorized files
        # create parser and read ini configuration file
        authorized_files_parser = configparser.ConfigParser()
        authorized_files_parser.read(constantes.CONFIG_AUTHORIZED_FILES_INI)
        dict_authorized_files = {}  # Init d'un dico des fichiers autorisés
        if authorized_files_parser.has_section(section_ini_authorized_files):
            authorized_files_items = authorized_files_parser.items(section_ini_authorized_files)
            for authorized_files_item in authorized_files_items:
                dict_authorized_files[authorized_files_item[0]] = authorized_files_item[1]
        else:
            raise Exception(f'Error from finder file : Section {section_ini_authorized_files} not found in the {constantes.CONFIG_AUTHORIZED_FILES_INI} file.')
        return list(dict_authorized_files.values())

    def reset_progressbar_statusbar(self):
        self.progressBar.reset()
        # self.progressBar.hide()
        self.statusBar.showMessage("")

    def see_about(self):
        try:
            with open(os.path.join('data/about.txt'), 'r') as file_about:
                # self.textEdit.setText(f.read())
                message_box_about = QtWidgets.QMessageBox()
                message_box_about.setWindowTitle("A propos de Finder")
                message_box_about.setText(file_about.read())
                # message_box_about.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # Pouvoir sélectionner par la souris ce qu'il y a dans le messageBox
                # Changer l'icone de la message_box
                QPixmap.pixmap = QPixmap("icons/about.png")
                message_box_about.setWindowIcon(QIcon(QPixmap.pixmap))
                # Afficher la message box
                message_box_about.exec()
        except IOError:
            logging.debug("File retrieving error...")
            self.textEdit.setText("File retrieving error...")

    def list_authorized_files(self):
        self.authorized_files_vmware_source_list = self.read_authorized_files_config("authorized_files_vmware")
        self.authorized_files_opca_source_list = self.read_authorized_files_config("authorized_files_opca")
        self.authorized_files_cmdb_source_list = self.read_authorized_files_config("authorized_files_cmdb")
        self.authorized_files_cmdb_all_source_list = self.read_authorized_files_config("authorized_files_cmdb_all")
        self.authorized_files_source_list = self.authorized_files_vmware_source_list + self.authorized_files_opca_source_list + self.authorized_files_cmdb_source_list + self.authorized_files_cmdb_all_source_list

    def display_list_authorized_files(self):
        self.list_authorized_files()
        authorized_files_source_list_cr = "\n".join(self.authorized_files_source_list)
        # self.textEdit.setText(f"Fichiers d'exports autorisés à être importés dans la base :\n\n{str(authorized_files_source_list_cr)}")
        message_box_authorized_files = QtWidgets.QMessageBox()
        message_box_authorized_files.setWindowTitle("Liste des fichiers autorisés à être importés dans la base :")
        message_box_authorized_files.setStyleSheet("QLabel{min-width: 400px;}")  # Donner une largeur à la message box car sinon on ne voit pas le titre en entier
        message_box_authorized_files.setText(str(authorized_files_source_list_cr))
        # message_box_authorized_files.setIcon(QtWidgets.QMessageBox.Information)  # Affiche un icon "information" dans la box
        message_box_authorized_files.icon()  #
        # message_box_authorized_files.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)  # Pouvoir sélectionner par la souris ce qu'il y a dans le messageBox
        # Changer l'icone de la message_box
        QPixmap.pixmap = QPixmap("icons/list.png")
        message_box_authorized_files.setWindowIcon(QIcon(QPixmap.pixmap))
        # Afficher la message box
        message_box_authorized_files.exec()

    def display_list_last_modifications_exports(self):
        self.get_export_folder_date("vmware")  # Récupérer la date du répertoire d'exports vmware
        self.get_export_folder_date("opca")  # Récupérer la date du répertoire d'exports opca
        self.get_export_folder_date("cmdb")  # Récupérer la date du répertoire d'exports cmdb
        self.get_export_folder_date("cmdb_all")  # Récupérer la date du répertoire d'exports cmdb_all
        self.exports_folders_dates = self.result_folder_vmware + "\n\n" + self.result_folder_opca + "\n\n" + self.result_folder_cmdb + "\n\n" + self.result_folder_cmdb_all
        message_box_dates_exports = QtWidgets.QMessageBox()
        message_box_dates_exports.setWindowTitle("Dates des dernières modifications des exports :")
        message_box_dates_exports.setText(f"{self.exports_folders_dates}")
        message_box_dates_exports.setStyleSheet("QLabel{min-width: 300px;}")  # Donner une largeur à la message box car sinon on ne voit pas le titre en entier
        # Changer l'icone de la message_box
        QPixmap.pixmap = QPixmap("icons/list.png")
        message_box_dates_exports.setWindowIcon(QIcon(QPixmap.pixmap))
        # Afficher la message box
        message_box_dates_exports.exec()

    def setup_connections(self):
        # Setup of connections between widgets and other functions
        self.pushButton.clicked.connect(self.search)
        self.pushButton_2.clicked.connect(self.import_list)
        # Make the button an image
        search_icon = QtGui.QPixmap("icons/search.png")
        list_icon = QtGui.QPixmap("icons/list.png")
        self.pushButton.setIcon(search_icon)
        self.pushButton_2.setIcon(list_icon)
        # ComboBox = drop-down menu
        self.comboBox.addItems(["Equipement", "Host (ESXi ou CN)", "Application"])

    def setup_checkbox(self):
        if constantes.CHECKBOX_DATACENTER == False:
            self.checkBox_datacenter.setCheckState(QtCore.Qt.Unchecked)  
        else:
            self.checkBox_datacenter.setCheckState(QtCore.Qt.Checked)

        if constantes.CHECKBOX_CLUSTER == False:
            self.checkBox_cluster.setCheckState(QtCore.Qt.Unchecked)  
        else:
            self.checkBox_cluster.setCheckState(QtCore.Qt.Checked) 

        if constantes.CHECKBOX_ANNOTATION== False:
            self.checkBox_annotation.setCheckState(QtCore.Qt.Unchecked)  
        else:
            self.checkBox_annotation.setCheckState(QtCore.Qt.Checked)       
        
    def create_database_and_tables(self):
        """ Creates database and tables """
        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
        time.sleep(2)  # The connection is sometimes so fast that there is no time to display the text that indicates the connection
        with DatabaseGestionSqlite() as db_connection:  # "with" allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                logging.debug("Creating database and its tables if they do not already exist.")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                time.sleep(2)  # The connection is sometimes so fast that there is no time to display the text that indicates the connection
                db_connection.sql_query_execute("BEGIN TRANSACTION;")
                db_connection.sql_query_execute("CREATE TABLE IF NOT EXISTS 'serveur_vmware' ('serveur_name' text, 'dns_name' text,'host_name' text, 'management_name' text, 'datacenter_name' TEXT, 'cluster_name' TEXT, 'annotation' TEXT);")
                db_connection.sql_query_execute("CREATE TABLE IF NOT EXISTS 'serveur_opca' ('serveur_name' text, 'dns_name' text, 'host_name' text, 'management_name' text);")
                db_connection.sql_query_execute("CREATE TABLE IF NOT EXISTS 'serveur_cmdb' ('serveur_name' TEXT, 'environment_name' TEXT, 'device_type' TEXT, 'operational_status' TEXT, 'system_type' TEXT, 'asset' TEXT);")
                db_connection.sql_query_execute("CREATE TABLE IF NOT EXISTS 'serveur_cmdb_all' ('serveur_name' TEXT, 'environment_name' TEXT, 'device_type' TEXT, 'operational_status' TEXT, 'system_type' TEXT);")
                db_connection.sql_query_execute("COMMIT;")
                if db_connection.error_db_execution is None:
                    logging.debug("Database and its tables have been created if they didn't not already exist.")
                else:
                    logging.debug(db_connection.error_db_execution)
            else:
                logging.debug(db_connection.error_db_connection)

    def check_if_exports_exist(self, export_type):
        # Check if there are any exports in the folder concerned
        if not os.listdir(fr"{constantes.EXPORTS_DIR}\exports_{export_type}"):
            main_window.textEdit.setText(f"Le répertoire des exports exports_{export_type} est vide.\nLa mise à jour de la base de données ne peut pas être lancée.")
            logging.debug(f"The exports folder exports_{export_type} is empty.")
            return False
        else:
            logging.debug(f"The exports folder exports_{export_type} is not empty.")           
            return True

    def update_db(self, export_type):
        """ Updates the bdd according to the files in the export folder.
           Warning, if there is no authorized file, the database will be reset to 0 (because we first drop the database)
           The principle is that the bdd is iso with the export folder
           """
        self.reset_progressbar_statusbar()
        data_list = []
        list_data_cmdb = []
        df_cmdb = None
        files_paths_authorized_list = []

        logging.debug(f"Checking before updating that exports folder {export_type} is not empty.")
        if self.check_if_exports_exist(export_type) == False:  # If exports folder is empty then we leave the function (we don't update because the update function starts by delete all entries)
            return False      

        # Creates a list of files that are in the export folder where each element is of the type 'C:\\path\file.ext'
        files_paths_list = []
        exports_files_folder_path = fr"{constantes.EXPORTS_DIR}\exports_{export_type}"  # Retrieving the path of the export folder
        for root, dirs, files in os.walk(exports_files_folder_path):
            for file in files:
                files_paths_list.append(os.path.join(root, file))

        for file_path in files_paths_list:
            logging.debug(file_path)
            file = os.path.basename(file_path)
            logging.debug(file)
            file_is_authorized = self.is_file_authorized(file)
            if file_is_authorized:
                files_paths_authorized_list.append(file_path)
                logging.debug(files_paths_authorized_list)
            else:
                main_window.textEdit.setText(f"Le fichier '{file}' n'est pas un fichier authorisé à être importé dans la base de données.\nImportation en cours annulée.\nVeuillez supprimer ou renommer ce fichier et recommencer.\nConsultez la liste des fichiers autorisés dans le menu 'Paramètres' puis 'Lister les fichiers autorisés'.")
                return False

        logging.debug(export_type)
        if export_type in ["opca", "vmware"]:
            # Create list of list from vmware and opca export files
            files_paths_authorized_list_len = len(files_paths_authorized_list)
            step = 0
            logging.debug(files_paths_authorized_list_len)
            for file_number, file_path_authorized in enumerate(files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                logging.debug(format(file_authorized))
                main_window.textEdit.setText(f"Récupération des données depuis le fichier {format(file_authorized)}...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                file_name_authorized = os.path.splitext(file_authorized)[0]

                # Update of the progress bar
                main_window.progressBar.show()
                pourcentage_number = (file_number * 100 - 1) // files_paths_authorized_list_len
                for between_pourcentage in range(step, pourcentage_number):
                    time.sleep(0.02)
                    main_window.statusBar.showMessage(f"Action en cours de {between_pourcentage}% ...")
                    main_window.progressBar.setValue(between_pourcentage)
                    step = (file_number * 100 - 1) // files_paths_authorized_list_len

                if export_type == "opca":
                    df = pandas.read_csv(file_path_authorized, sep=';')
                    # Add a column to the dataframe
                    df['DNS Name'] = "N/A"
                    # Add a column to the dataframe
                    df['management'] = file_name_authorized
                    # The dataframe will contains only these colums
                    df = df[["Machine Virtuelle", "DNS Name", "management", "Compute Node"]]

                else:
                    df = pandas.read_excel(file_path_authorized)
                    # Add a column to the dataframe
                    df['management'] = file_name_authorized
                    # The dataframe will contains only these colums
                    df = df[["VM", "DNS Name", "management", "Host", "Datacenter", "Cluster", "Annotation"]]

                # df = df.where((pandas.notnull(df)), 'N/A')  # Remplacer les 'nan' (générés par panda quand il n'y a pas de valeur dans la case excel) par des 'N/A' sinon SQL traitera les 'nan' comme des '0'
                list_data_temp = df.values.tolist()
                data_list.extend(list_data_temp)
            logging.debug(data_list)  # Donne une liste de listes
        elif export_type == "cmdb":
            # Create list of list from cmdb export file
            # print(files_paths_authorized_list)
            list_data_cmdb = []
            files_paths_authorized_list_len = len(files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                main_window.textEdit.setText(f"Data retrieval from the file {format(file_authorized)}...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                # Update of the progress bar
                main_window.progressBar.show()
                pourcentage_number = (file_number * 100 - 1) // files_paths_authorized_list_len
                for between_pourcentage in range(step, pourcentage_number):
                    time.sleep(0.02)
                    main_window.statusBar.showMessage(f"Processing of {between_pourcentage}% ...")
                    main_window.progressBar.setValue(between_pourcentage)
                    step = (file_number * 100 - 1) // files_paths_authorized_list_len

                    df_cmdb = pandas.read_csv(file_path_authorized, sep=',', encoding="Windows-1252")
                    # The dataframe will contains only these colums
                    df_cmdb = df_cmdb[["ci6_name", "ci2_name", "ci6_u_device_type", "ci6_operational_status", "ci6_sys_class_name", "ci6_asset_tag"]]

                # df_cmdb = df_cmdb.where((pandas.notnull(df_cmdb)), 'N/A')  # Remplacer les 'nan' (générés par panda quand il n'y a pas de valeur dans la case excel) par des 'N/A' sinon SQL traitera les 'nan' comme des '0'
                list_data_cmdb_temp = df_cmdb.values.tolist()
                # print(list_data_cmdb_temp)
                list_data_cmdb.extend(list_data_cmdb_temp)
                # print(list_data_cmdb)

        elif export_type == "cmdb_all":
            # Create list of list from cmdb export file
            # print(files_paths_authorized_list)
            list_data_cmdb_all = []
            files_paths_authorized_list_len = len(files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                main_window.textEdit.setText(f"Data retrieval from the file {format(file_authorized)}...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI

                # Update of the progress bar
                main_window.progressBar.show()
                pourcentage_number = (file_number * 100 - 1) // files_paths_authorized_list_len
                for between_pourcentage in range(step, pourcentage_number):
                    time.sleep(0.02)
                    main_window.statusBar.showMessage(f"Processing of {between_pourcentage}% ...")
                    main_window.progressBar.setValue(between_pourcentage)
                    step = (file_number * 100 - 1) // files_paths_authorized_list_len

                    df_cmdb_all = pandas.read_csv(file_path_authorized, sep=',', encoding="Windows-1252")
                    # The dataframe will contains only these colums
                    df_cmdb_all = df_cmdb_all[["name", "u_platform_type", "u_device_type", "operational_status", "sys_class_name"]]

                # df_cmdb_all = df_cmdb_all.where((pandas.notnull(df_cmdb_all)), 'N/A')  # Remplacer les 'nan' (générés par panda quand il n'y a pas de valeur dans la case excel) par des 'N/A' sinon SQL traitera les 'nan' comme des '0'
                list_data_cmdb_all_temp = df_cmdb_all.values.tolist()
                # print(list_data_cmdb_all_temp)
                list_data_cmdb_all.extend(list_data_cmdb_all_temp)
                # print(list_data_cmdb_all)

        main_window.textEdit.setText("Connexion à la base...")
        QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
        time.sleep(2)  # The connection is sometimes so fast that there is no time to display the text that indicates the connection
        with DatabaseGestionSqlite() as db_connection:  # "with" allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                logging.debug("DELETE FROM serveur_" + export_type)
                db_connection.sql_query_execute("DELETE FROM serveur_" + export_type)
                main_window.textEdit.setText(f"Insertion des données de {export_type} dans la base...")
                QtWidgets.QApplication.processEvents()  # Force a refresh of the UI
                if export_type == "cmdb":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_cmdb (serveur_name, environment_name, device_type, operational_status, system_type, asset) VALUES (?,?,?,?,?,?)", list_data_cmdb)
                elif export_type == "cmdb_all":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_cmdb_all (serveur_name, environment_name, device_type, operational_status, system_type) VALUES (?,?,?,?,?)", list_data_cmdb_all)

                elif export_type == "opca":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_opca (serveur_name, dns_name, management_name, host_name) VALUES (?,?,?,?)", data_list)
                elif export_type == "vmware":
                    logging.debug(data_list)
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_vmware (serveur_name, dns_name, management_name, host_name, datacenter_name, cluster_name, annotation) VALUES (?,?,?,?,?,?,?)", data_list)
                if db_connection.error_db_execution is None:
                    main_window.textEdit.setText(f"La base de données {export_type} contient {str(db_connection.cursor.rowcount)} lignes.")
                    main_window.progressBar.setValue(100)  # 100 -> 100%
                    main_window.statusBar.showMessage("Mise à jour de la base de données terminée !")
                else:
                    logging.debug(db_connection.error_db_execution)
                    main_window.textEdit.setText("Erreur lors de l'insertion des données dans la base.")
            else:
                logging.debug(db_connection.error_db_connection)
                main_window.textEdit.setText("Erreur de connexion à la base de données.")
            main_window.reset_progressbar_statusbar()
        

    def setup_keyboard_shortcuts(self):
        # We create a shortcut for the Esc key that will close the application
        QtGui.QShortcut(QtGui.QKeySequence('Esc'), self, self.close)
        # A shortcut is created for the ENTER key on the numeric keypad that will launch the search
        QtGui.QShortcut(QtGui.QKeySequence('Enter'), self, self.search)
        # We create a shortcut for the ENTER key on the keyboard that will launch the search
        QtGui.QShortcut(QtGui.QKeySequence('Return'), self, self.search)

    def search(self):
        #self.reset_progressbar_statusbar()
        search_string = self.lineEdit.text()
        logging.debug(f"search_string : {search_string}")
        search_list = search_string.split()
        logging.debug(f"search_list : {search_list}")
        search_choice = self.comboBox.currentText()
        logging.debug(f"search_choice : {search_choice}")
        logging.debug("Création du thread de recherche")  
        self.search_thread(search_list, search_choice)

    def search_thread(self, search_list, search_choice):
        self.thread = QtCore.QThread(self)
        self.search_instance = Search(search_list, search_choice)
        self.search_instance.moveToThread(self.thread)
        self.search_instance.searched_string_signal.connect(self.searched_string_if_signal) 
        self.search_instance.signal_results_query_search.connect(self.display_in_tableview)
        self.search_instance.signal_display_warning_box.connect(self.display_warning_box)
        self.search_instance.signal_textEdit_setText.connect(self.set_text_in_edit_text_if_signal)
        #self.search_instance.finished.connect(self.thread.quit)
        self.search_instance.finished.connect(self.finished_if_signal)
        self.thread.started.connect(self.search_instance.search)
        self.thread.start()
        # Création de la barre de progression en fenêtre        

        self.prg_dialog = QtWidgets.QProgressDialog("Recherche en cours...", "Annuler...", 1, len(search_list) + 1)
        self.prg_dialog.close()
        self.prg_dialog.canceled.connect(self.abort)
        if len(search_list) > 1:
            self.prg_dialog.show()

    def display_warning_box(self, warning_title, warning_text):
        self.prg_dialog.hide()
        logging.debug("Signal recherche vide reçu.")
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, f"{warning_title}", f"{warning_text}")
        msg_box.exec()
        self.search_instance.finished.connect(self.thread.quit)

    def abort(self):
        logging.debug(f"On a appuyé sur Annuler.")
        self.search_instance.runs = False
        self.thread.quit()
        
    def searched_string_if_signal(self, searched_string_signal):  # On exécute cette fonction quand le signal searched_string_signal du thread est émit et on récupère la valeur envoyée par le signal
        logging.debug(f"On a reçu le signal pour {searched_string_signal} pour incrémenter la barre de progression")
        self.prg_dialog.setValue(self.prg_dialog.value() + 1)  # Mise à jour de la barre de progression
        main_window.textEdit.setText(f"Recherche en cours pour : {searched_string_signal}")

    def finished_if_signal(self):
        logging.debug(f"Traitement terminé. On quitte le thread")
        self.thread.quit()
        self.prg_dialog.setValue(self.prg_dialog.value() + 1)  # Mise à jour de la barre de progression
        
    def set_text_in_edit_text_if_signal(self, text_to_set_in_edit_text):
        main_window.textEdit.setText(f"{text_to_set_in_edit_text}")
        
    def import_list(self):        
        self.window_import_list = ImportList(main_window)
        self.reset_progressbar_statusbar()
        self.window_import_list.show()        

    def list_exports(self, export_type):
        # Check if there are any exports in the folder concerned
        if not os.listdir(fr"{constantes.EXPORTS_DIR}\exports_{export_type}"):
            main_window.textEdit.setText(f"Le répertoire des exports exports_{export_type} est vide.")
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
                
            #files_not_authorized_list.remove('.gitkeep')  # Ne pas afficher les fichiers .gitkeep comme des fichiers non-autorisés /!\ Créé une erreur si le fichier n'existe pas

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

            main_window.textEdit.setText(f"{result_search_authorized}\n\n{result_search_not_authorized}")

    def is_file_authorized(self, file):
        """ If the file is in the list of authorized_files, we copy the file
        :param file: Name of the file with its extension
        :return: A booleen True if the file is part of the authorized list or False if not
        """

        if file in main_window.authorized_files_source_list:  # Lire l'attribut de l'instance qui a déjà été initialisé
            logging.debug(f"is_file_authorized : \"{file}\" is an authorized file.")
            file_authorized = True
        else:
            logging.debug(f"is_file_authorized : \"{file}\" is not an authorized file.")
            file_authorized = False

        return file_authorized


    def display_in_tableview(self, results_query_search, search_choice):
        # Display data results in tableview
        # header table view

        logging.debug(f"search_choice : {search_choice}")

        if search_choice == 'Equipement':
            header = ['Nom', 'vCenter ou ESXi (vmware), Management Node (opca)', 'Datacenter (vmware)', 'Cluster (vmware)', 'Nom DNS (vmware)', 'Annotation (vmware)', 'Environnement/Application (CMDB)', 'Type (CMDB)', 'Status opérationnel (CMDB)', 'Type de Système (CMDB)', 'Asset (CMDB)']

        elif search_choice == 'Host (ESXi ou CN)':
            header = ['Nom de l\'ESXi (vmware) ou du Management Node (opca)', 'vCenter (vmware) ou Management Node (opca)']

        elif search_choice == 'Application':
            header = ['Application (CMDB)', 'Nom']

        # Create instance table view
        table_model = MyTableModel.MyTableModel(results_query_search, header, window_instance=main_window)
        main_window.tableView.setModel(table_model)
        
        # install event filter pour pouvoir récupérer un évenement d'appui de CTRL+C (copy) quand on a sélectionné des cellules
        main_window.tableView.installEventFilter(table_model)
        # set color and style header
        # stylesheet = "::section{Background-color:rgb(179, 224, 229);border-radius:14px;}"   # Pour ne pas avoir les bordures des cases du header
        stylesheet = "::section{Background-color:rgb(179, 224, 229)}"  # Couleur bleu ciel pour l'entête du tableau
        main_window.tableView.horizontalHeader().setStyleSheet(stylesheet)
        # set font
        # font = QtGui.QFont("Courier New", 14)
        # self.tableView.setFont(font)
        # main_window.tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)  # Ajuster la zone tableview aux colonnes (ne fonctionne pas ??!)
        # set column width to fit contents (set font first!)
        main_window.tableView.resizeColumnsToContents()
        # stretch the last column to the view so that the table view fit the layout
        main_window.tableView.horizontalHeader().setStretchLastSection(True)
        delegate = AlignDelegate.AlignDelegate(main_window.tableView)
        # main_window.tableView.setItemDelegateForColumn(2, delegate)  # Pour Centrer le texte de la colonne id 2 (donc la troisième)
        main_window.tableView.setItemDelegate(delegate)  # for all columns
        # enable sorting
        main_window.tableView.setSortingEnabled(True)
        #main_window.statusBar.showMessage(f"Résultats : {str(nbr)} | OK : {str(nbr_result_ok)} | KO : {str(nbr_result_ko)}")
        main_window.progressBar.reset()
        # main_window.progressBar.hide()

        main_window.textEdit.setText("Sélectionnez des cellules puis CTRL+C pour les copier.\n\nFaites CTRL+A pour sélectionner toutes les données puis CTRL+C puis CTRL+V pour coller dans un notepad.\nLes données seront automatiquement formatées en CSV (avec des ';').\n\nVous pouvez également trier les colonnes directement dans l'interface.")

        # # Cacher des colonnes  # TPO
        # if main_window.checkBox_datacenter.isChecked() == False:
        #     main_window.tableView.hideColumn(2)
        # if main_window.checkBox_cluster.isChecked() == False:
        #     main_window.tableView.hideColumn(3)
        # if main_window.checkBox_annotation.isChecked() == False:
        #     main_window.tableView.hideColumn(5)
  
# MAIN

app = QtWidgets.QApplication([])
main_window = Window()
app.exec()
