import logging
import sqlite3
import traceback
import sys

import constantes


class DatabaseGestionSqlite:
    def __init__(self):
        self.filename = constantes.DB_SQLITE_FILE
        self.conn = None
        self.cursor = None
        self.error_db_connection = None  # By default there is no connection error
        self.error_db_execution = None

    def __enter__(self):
        logging.debug("DatabaseGestionSqlite class def __enter__ context manager")
        logging.debug("Connection to database.")
        try:
            self.conn = sqlite3.connect(self.filename)  # Create database if doesn't already exist 
            #self.conn = sqlite3.connect(f'file:{self.filename}?mode=rw', uri=True)  # Open database file in rw mode but raise error if doesn't exist
            self.cursor = self.conn.cursor()
        except sqlite3.Error as er:
            self.error_db_connection = str(er)
            logging.debug('SQLite error: %s' % (' '.join(er.args)))
            # print("Exception class is: ", er.__class__)  # Ne semble rien afficher et avec logging fait une erreur python
            logging.debug('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.debug(traceback.format_exception(exc_type, exc_value, exc_tb))
        return self  # We return the object otherwise in with there will be no object. With the use of with and the context manager, it is what __enter__ returns that is taken into account.

    def __exit__(self, *args):
        logging.debug("DatabaseGestionSqlite class def __exit__ context manager")
        if not self.error_db_connection:
            self.disconnect_db()

    def disconnect_db(self):
        self.cursor.close()
        self.conn.close()
        logging.debug("Disconnected from database.")

    def sql_query_execute(self, sql):
        try:
            self.cursor.execute(sql)
        except sqlite3.Error as er:
            self.error_db_execution = str(er)
            logging.debug('SQLite error: %s' % (' '.join(er.args)))
            # print("Exception class is: ", er.__class__)  # Ne semble rien afficher et avec logging fait une erreur python
            logging.debug('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.debug(traceback.format_exception(exc_type, exc_value, exc_tb))

    def sql_query_executemany(self, sql, datalist):
        try:
            self.cursor.executemany(sql, datalist)
            self.conn.commit()
        except sqlite3.Error as er:
            self.error_db_execution = str(er)
            logging.debug('SQLite error: %s' % (' '.join(er.args)))
            # print("Exception class is: ", er.__class__)  # Ne semble rien afficher et avec logging fait une erreur python
            logging.debug('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logging.debug(traceback.format_exception(exc_type, exc_value, exc_tb))

    def rows(self):
        return self.cursor.rowcount