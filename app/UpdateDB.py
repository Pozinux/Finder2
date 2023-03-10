import logging
import os
import time
import pandas

from PySide6 import QtCore

import AlignDelegate
import DatabaseGestionSqlite
import MyTableModel
import constantes

from DatabaseGestionSqlite import DatabaseGestionSqlite


class UpdateDB(QtCore.QObject):

    finished = QtCore.Signal()  # Signal pour fin du Thread
    signal_file_authorized = QtCore.Signal(object)
    signal_textEdit_setText = QtCore.Signal(object)
    signal_results_update_db = QtCore.Signal(object)
    

    def __init__(self, export_type, files_paths_authorized_list):
        super().__init__()

        self.export_type = export_type
        self.files_paths_authorized_list = files_paths_authorized_list

    def update_db(self):

        data_list = []
        list_data_cmdb = []
        df_cmdb = None

        print("is executed main thread?",  QtCore.QThread.currentThread() is QtCore.QCoreApplication.instance().thread())  # Pour vérifier si on est dans le main thread

        if self.export_type in ["opca", "vmware"]:
            # Create list of list from vmware and opca export files
            files_paths_authorized_list_len = len(self.files_paths_authorized_list)
            step = 0
            logging.debug(f"files_paths_authorized_list_len : {files_paths_authorized_list_len}")

            for file_number, file_path_authorized in enumerate(self.files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                logging.debug(f"format(file_authorized) : {format(file_authorized)}")
                file_name_authorized = os.path.splitext(file_authorized)[0]
                self.signal_file_authorized.emit(file_authorized)

                if self.export_type == "opca":
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

        elif self.export_type == "cmdb":
            # Create list of list from cmdb export file
            # print(files_paths_authorized_list)
            list_data_cmdb = []
            files_paths_authorized_list_len = len(self.files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(self.files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                self.signal_file_authorized.emit(file_authorized)
                df_cmdb = pandas.read_csv(file_path_authorized, sep=',', encoding="Windows-1252")
                df_cmdb = df_cmdb[["ci6_name", "ci2_name", "ci6_u_device_type", "ci6_operational_status", "ci6_sys_class_name", "ci6_asset_tag"]]  # The dataframe will contains only these colums
                list_data_cmdb_temp = df_cmdb.values.tolist()
                list_data_cmdb.extend(list_data_cmdb_temp)

        elif self.export_type == "cmdb_all":
            # Create list of list from cmdb export file
            list_data_cmdb_all = []
            files_paths_authorized_list_len = len(self.files_paths_authorized_list)
            step = 0
            for file_number, file_path_authorized in enumerate(self.files_paths_authorized_list, 1):
                file_authorized = os.path.basename(file_path_authorized)
                self.signal_file_authorized.emit(file_authorized)
                df_cmdb_all = pandas.read_csv(file_path_authorized, sep=',', encoding="Windows-1252")
                df_cmdb_all = df_cmdb_all[["name", "u_platform_type", "u_device_type", "operational_status", "sys_class_name"]]  # The dataframe will contains only these colums
                list_data_cmdb_all_temp = df_cmdb_all.values.tolist()
                list_data_cmdb_all.extend(list_data_cmdb_all_temp)

        self.signal_textEdit_setText.emit("Connexion à la base...")
        
        with DatabaseGestionSqlite() as db_connection:  # "with" allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:
                logging.debug("DELETE FROM serveur_" + self.export_type)
                db_connection.sql_query_execute("DELETE FROM serveur_" + self.export_type)
                self.signal_textEdit_setText.emit(f"Insertion des données de {self.export_type} dans la base...")
                time.sleep(5)
                if self.export_type == "cmdb":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_cmdb (serveur_name, environment_name, device_type, operational_status, system_type, asset) VALUES (?,?,?,?,?,?)", list_data_cmdb)
                elif self.export_type == "cmdb_all":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_cmdb_all (serveur_name, environment_name, device_type, operational_status, system_type) VALUES (?,?,?,?,?)", list_data_cmdb_all)

                elif self.export_type == "opca":
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_opca (serveur_name, dns_name, management_name, host_name) VALUES (?,?,?,?)", data_list)
                elif self.export_type == "vmware":
                    logging.debug(data_list)
                    db_connection.sql_query_executemany(f"INSERT INTO serveur_vmware (serveur_name, dns_name, management_name, host_name, datacenter_name, cluster_name, annotation) VALUES (?,?,?,?,?,?,?)", data_list)
                if db_connection.error_db_execution is None:
                    self.signal_textEdit_setText.emit(f"Mise à jour terminée !\n\nLa base de données {self.export_type} contient {str(db_connection.cursor.rowcount)} lignes.")  
                else:
                    logging.debug(db_connection.error_db_execution)
                    self.signal_textEdit_setText.emit("Erreur lors de l'insertion des données dans la base.")
            else:
                logging.debug(db_connection.error_db_connection)
                self.signal_textEdit_setText.emit("Erreur de connexion à la base de données.")

        logging.debug("On envoie le signal de fin de thread de mise à jour")
        self.finished.emit() # Indique que le Thread a terminé son travail