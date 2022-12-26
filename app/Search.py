import logging
import os
import time

from PySide6 import QtCore

import AlignDelegate
import DatabaseGestionSqlite
import MyTableModel
import constantes


class Search(QtCore.QObject):

    finished = QtCore.Signal()  # Signal pour fin du Thread
    searched_string_signal = QtCore.Signal(object)  # On créé un signal pour envoyer le mot cherché en cours vers la fenêtre principale
    signal_results_query_search = QtCore.Signal(object, object)  # On créé un signal pour envoyer le résultat de la recherche vers la fenêtre principale
    signal_textEdit_setText = QtCore.Signal(object)  # On créé un signal pour envoyer une string vers la fenêtre principale
    signal_display_warning_box = QtCore.Signal(object, object)  # On créé un signal pour envoyer un titre et un texte pour une popup warning vers la fenêtre principale
    

    def __init__(self, list_to_search, categorie_to_search_in):
        super().__init__()

        self.search_list = list_to_search
        self.categorie_to_search_in = categorie_to_search_in
        self.list_result_saut = []
        self.runs = True

    def search(self):

        print("is executed main thread?",  QtCore.QThread.currentThread() is QtCore.QCoreApplication.instance().thread())  # Pour vérifier si on est dans le main thread

        results_query_search = []
        logging.debug(f"self.categorie_to_search_in: {self.categorie_to_search_in}")

        with DatabaseGestionSqlite.DatabaseGestionSqlite() as db_connection:  # with allows you to use a context manager that will automatically call the disconnect function when you exit the scope
            if db_connection.error_db_connection is None:

                if self.is_db_empty():
                    pass
                else:
                    logging.debug(f"La base de données n'est pas vide")
                    logging.debug(f"self.search_list: {self.search_list}")

                    if not self.search_list:  # If search is empty
                        logging.debug(f"Rien n'a été entré dans la barre de recherche")
                        self.signal_display_warning_box.emit("Recherche vide", "Veuillez entrer une recherche.\nPar exemple :\n\n- Server1\n- Serv\n- server1.domain\n- appli_toto\n- server1 server2 server3")
                        self.runs = False
                        return False

                    else:  # Si on a bien donné des éléments à rechercher
                        search_list_len = len(self.search_list)
                        logging.debug(f"La barre de recherche contient {search_list_len} éléments à rechercher")
                        step_search = 0
                        for file_number_search, search_string in enumerate(self.search_list, 1):
                            if not self.runs:  # Si on a appuyé sur Annuler, on ferme le thread proprement mais il continue de tourner pour finir sa tâche donc on met un flag pour lui dire qu'on a appuyé sur Annuler
                                self.signal_textEdit_setText.emit("Recherche annulée !")
                                return False
                            else:
                                search_string = str.strip(search_string)  # delete spaces before and after the string

                                if self.categorie_to_search_in == 'Equipement':
                                    sql_query_execute = f"""
                                                            select DISTINCT t.serveur_name,
                                                                    coalesce(v.management_name, o.management_name, 'N/A') management_name,                                           
                                                                    coalesce(v.datacenter_name, 'N/A') datacenter_name,
                                                                    coalesce(v.cluster_name, 'N/A') cluster_name,
                                                                    coalesce(v.dns_name, o.dns_name, 'N/A') dns_name,
                                                                    coalesce(v.annotation, 'N/A') annotation,
                                                                    coalesce(c.environment_name, ca.environment_name, 'N/A') environment_name,
                                                                    coalesce(c.device_type, ca.device_type, 'N/A') device_type,
                                                                    coalesce(c.operational_status, ca.operational_status, 'N/A') operational_status,
                                                                    coalesce(c.system_type, ca.system_type, 'N/A') system_type,
                                                                    coalesce(c.asset, 'N/A') asset
                                                                from (
                                                                select upper(serveur_name) serveur_name from serveur_cmdb_all union
                                                                select upper(serveur_name) serveur_name from serveur_cmdb union
                                                                select upper(serveur_name) from serveur_vmware union
                                                                select upper(serveur_name) from serveur_opca
                                                                ) t
                                                                left join serveur_cmdb_all ca on ca.serveur_name = t.serveur_name COLLATE NOCASE
                                                                left join serveur_cmdb c on c.serveur_name = t.serveur_name COLLATE NOCASE
                                                                left join serveur_vmware v on v.serveur_name = t.serveur_name COLLATE NOCASE
                                                                left join serveur_opca o on o.serveur_name = t.serveur_name COLLATE NOCASE
                                                            WHERE v.dns_name LIKE \'%{search_string}%\' 
                                                                OR v.serveur_name LIKE \'%{search_string}%\'
                                                                OR o.dns_name LIKE \'%{search_string}%\' 
                                                                OR o.serveur_name LIKE \'%{search_string}%\'
                                                                OR c.serveur_name LIKE \'%{search_string}%\'
                                                                OR ca.serveur_name LIKE \'%{search_string}%\'
                                                            """
                                elif self.categorie_to_search_in == 'Host (ESXi ou CN)':
                                    sql_query_execute = f"""SELECT 
                                                            host_name, 
                                                            management_name 
                                                            FROM serveur_opca 
                                                            WHERE host_name 
                                                            LIKE \'%{search_string}%\'"""

                                elif self.categorie_to_search_in == 'Application':
                                    sql_query_execute = f"""select DISTINCT c.environment_name,
                                                            t.serveur_name
                                                            from (
                                                            select serveur_name from serveur_cmdb union
                                                            select serveur_name from serveur_vmware union
                                                            select serveur_name from serveur_opca
                                                            ) t
                                                            left join serveur_cmdb c on c.serveur_name = t.serveur_name
                                                            left join serveur_vmware v on v.serveur_name = t.serveur_name
                                                            left join serveur_opca o on o.serveur_name = t.serveur_name 
                                                            WHERE c.environment_name LIKE \'%{search_string}%\'"""

                                logging.debug(f"Recherche lancée pour {search_string} qui est l'élément à rechercher numéro {file_number_search}")
                                db_connection.sql_query_execute(sql_query_execute)
                                rows_result_sql = db_connection.cursor.fetchall()
                                logging.debug(f"rows_result_sql: {rows_result_sql}")
                                
                                if not rows_result_sql:
                                    logging.debug(f"La recherche SQL a retourné un résultat vide")

                                    # En cas de résultat KO, on a pas le même nombre de colonnes en fonction de la catégorie recherchée
                                    if self.categorie_to_search_in == 'Equipement':
                                        results_query_search.append((search_string, 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports', 'Non présent dans les exports'))
                                    elif self.categorie_to_search_in == 'Host (ESXi ou CN)':
                                        results_query_search.append((search_string, 'Non présent dans les exports'))
                                    elif self.categorie_to_search_in == 'Application':
                                        results_query_search.append((search_string, 'Non présent dans les exports'))
                                
                                if rows_result_sql:
                                    logging.debug(f"La recherche SQL a retourné un résultat")
                                    nbr_item_in_list = len(rows_result_sql)
                                    results_query_search.extend(rows_result_sql)

                                logging.debug(f"On emet le signal searched_string_signal en passant la search_string en cours -> {search_string}")
                                self.searched_string_signal.emit(search_string)  # On émet le signal quand on a recherché un nom de la liste donnée par l'utilisateur et on fourni ce nom à l'interface graphique
            else:
                self.signal_textEdit_setText.emit("Erreur de connexion à la base de données.")
                logging.debug(db_connection.error_db_connection)
            
        logging.debug("On envoie le signal de fin de thread de recherche")
        self.signal_results_query_search.emit(results_query_search, self.categorie_to_search_in)  # On envoie le résultat de la requête sql pour qu'il soit affiché dans le tableau tableview
        self.finished.emit() # Indique que le Thread a terminé son travail


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
                    self.signal_textEdit_setText.emit("Erreur lors de l'exécution des requêtes (Sélectionner les lignes VMware) sur la base de données.")
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
                    self.signal_textEdit_setText.emit("Erreur lors de l'exécution des requêtes (Sélectionner les lignes OPCA) sur la base de données.")
                    logging.debug(db_connection.error_db_execution)
            else:
                self.signal_textEdit_setText.emit("Erreur de connexion à la base de données.")
                logging.debug(db_connection.error_db_connection)