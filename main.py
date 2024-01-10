import logging
from database import database
from extdata import getdata
from tools import procdata

## Configuramos el formato de log
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
#logging.critical("castaña")

## Comprobamos que la bbdd existe
logging.info('Arranque script CRNODES')
logging.info('Comprobando si existe la BBDD crnodes.db en el directorio database')
if database.check_database_exist():
    logging.info('Encontrada BBDD')
    #print("existe")
else:
    logging.warning("La BBDD no existe")
    #print("no existe")