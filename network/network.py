import socket
import socks
import nmap
import json
import requests

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session


def check_port_ipv4(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((ip, port))
    if result == 0:
        sock.close()
        return True
    else:
        sock.close()
        return False
    
def check_port_ipv6(ip, port):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((ip, port))
    if result == 0:
        sock.close()
        return True
    else:
        sock.close()
        return False
    
def check_port_tor(ip, port):
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1",9050)
    socket.socket = socks.socksocket
    sock= socket.socket
    sock.settimeout(0.5)
    result = sock.connect_ex((ip, port))
    if result == 0:
        sock.close()
        return True
    else:
        sock.close()
        return False
    

def get_node_version(address, address_type, port):
    nm = nmap.PortScanner()
    if address_type == "IPv4":
        nm.scan('{}'.format(address), arguments='-Pn -p {} --script bitcoin-info'.format(port))
        scan_result = nm.analyse_nmap_xml_scan()
    elif address_type == "IPv6":
        nm.scan('{}'.format(address), arguments='-6 -Pn -p {} --script bitcoin-info'.format(port))
        scan_result = nm.analyse_nmap_xml_scan()
    try:
        info = scan_result['scan'][address]['tcp'][int(port)]['script']['bitcoin-info']
        try:
            user_agent= info.split('User Agent: ',1)[1]
            return user_agent
        except Exception as e:
            return "Error"
    except KeyError as e:
        return "Error"

def get_more_nodes(ip, port):
    nodict={}
    nm = nmap.PortScanner()
    scan_result = nm.scan('{}'.format(ip), arguments='-p {} --script bitcoin-getaddr'.format(port))
    #for key in scan_result['scan'][ip]['tcp'][int(port)]['script']['bitcoin-getaddr']:
    #    print(key)
    try:
        info = scan_result['scan'][ip]['tcp'][int(port)]['script']['bitcoin-getaddr']
        lines = info.split('\n')
        for line in lines:
            chunks = line.split()
            for chunk in chunks:
                if '-'in chunk or len(chunk)<10:
                    pass
                else:
                    node_address = chunk.rsplit(':',1)[0]
                    node_port = chunk.rsplit(':',1)[1]
                    nodict[node_address] = node_port
        return nodict
    except KeyError:
        return nodict
    
def scan_open_ports(address, address_type):
    port_list=[]
    nm = nmap.PortScanner()
    if address_type == "IPv4":
        scan_result= nm.scan('{}'.format(address), arguments='-Pn -p 21,22,80,443,2100,2200,8000,8080,8332,8333,9735')
    elif address_type == "IPv6":
        scan_result= nm.scan('{}'.format(address), arguments='-6 -Pn -p 21,22,80,443,2100,2200,8000,8080,8332,8333,9735')
    try:
        for key in scan_result['scan'][address]['tcp']:
            if scan_result['scan'][address]['tcp'][key]['state'] == 'open':
                port_list.append(key)
        return port_list
    except:
        return port_list

def send_notification(message):
    ## Token 6898511931:AAEtXtLXHxeFAibL_cQDGSaTQJxRmX6_gXs
    ## Chat id 11178412
    TOKEN = "6898511931:AAEtXtLXHxeFAibL_cQDGSaTQJxRmX6_gXs"
    chat_id = "11178412" # https://stackoverflow.com/questions/75116947/how-to-send-messages-to-telegram-using-python
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message