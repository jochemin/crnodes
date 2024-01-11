import logging
from database import database
from extdata import getdata
from tools import procdata
from network import network

## Configuramos el formato de log
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
#logging.critical("castaña")

## Comprobamos que la bbdd existe si no existe la creamos y metemos los primeros nodos
logging.info('Arranque script CRNODES')
logging.info('Comprobando si existe la BBDD crnodes.db en el directorio database')
if database.check_database_exist():
    logging.info('Encontrada BBDD')
    #print("existe")
else:
    logging.warning("La BBDD no existe")
    logging.info("Se creará la BBDD")
    database.create_database()
    logging.info("Base de datos creada correctamente")
    ## Cargamos los datos desde external data source (bitnodes)
    logging.info("Realizando primera carga en la BBDD")
    for address, port in getdata.bitnode_dict().items():
        address_type = procdata.check_ip_address_type(address)
        if address_type == "IPv4":
            if network.check_port(address, 80):
                logging.info("Detectado nodo con puerto abierto: "+address+":"+port)
                database.insert_new_node(address, address_type, port)
    