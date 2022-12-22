import os
import logging

# A décommenter pour voir les log dans tous les fichiers du projet où "constantes.py" a été importé.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - In %(filename)s - Line %(lineno)s - %(message)s')

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(CUR_DIR, "config")
CONFIG_AUTHORIZED_FILES_INI = os.path.join(CONFIG_DIR, "config_authorized_files.ini")
EXPORTS_DIR = os.path.join(CUR_DIR, "exports")
DATA_DIR = os.path.join(CUR_DIR, "data")
EXPORTS_VMWARE_DIR = os.path.join(EXPORTS_DIR, "exports_vmware")
EXPORTS_OPCA_DIR = os.path.join(EXPORTS_DIR, "exports_opca")
EXPORTS_CMDB_DIR = os.path.join(EXPORTS_DIR, "exports_cmdb")
EXPORTS_CMDB_ALL_DIR = os.path.join(EXPORTS_DIR, "exports_cmdb_all")
DB_SQLITE_FILE = os.path.join(DATA_DIR, "sqlite_db_file.db")
CHECKBOX_DATACENTER = True
CHECKBOX_CLUSTER = True
CHECKBOX_ANNOTATION = True

logging.debug(f"DB_SQLITE_FILE -> {DB_SQLITE_FILE}")
