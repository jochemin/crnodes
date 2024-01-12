import logging
import multiprocessing
import json
from database import database
from extdata import getdata
from tools import procdata
from network import network

## Configuramos el formato de log
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)

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
            if network.check_port(address, int(port)):
                logging.info("Detectado nodo con puerto abierto: "+address+":"+port)
                database.insert_new_node(address, address_type, port)
    
## tenemos datos en la bbdd, son equipos que aceptan conexiones entrantes.

## completamos la versión del cliente Bitcoin 
'''
node_list =database.no_user_agent()
for address, bitcoin_port in node_list:
    user_agent = network.get_node_version(address, bitcoin_port)
    if user_agent == 'Error':
        pass
    else:
        logging.info("Detectado "+user_agent+ " en "+ address)
        database.add_user_agent(address, user_agent)
'''

## escaneo puertos 

node_list = database.no_scan_date()
for node in node_list:
    open_port_list = network.scan_open_ports(node[0])
    database.add_open_ports(node[0], json.dumps(open_port_list))
    