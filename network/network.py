import socket
import nmap
import json

def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, port))
    if result == 0:
        sock.close()
        return True
    else:
        sock.close()
        return False

def get_node_version(ip, port):

    nm = nmap.PortScanner()
    nm.scan('{}'.format(ip), arguments='-p {} --script bitcoin-info'.format(port))
    #nm.scan('{}'.format(ip), arguments='-p 8333 --script bitcoin-info --script bitcoin-getaddr')
    #scan = nm.scan(ip, arguments='-p 8333 --script bitcoin-info --script bitcoin-getaddr')
    scan_result = nm.analyse_nmap_xml_scan()
    try:
        info = scan_result['scan'][ip]['tcp'][int(port)]['script']['bitcoin-info']
        return(info.split('User Agent: ',1)[1])
    except KeyError:
        return "Error"

def scan_open_ports(ip):
    port_list=[]
    nm = nmap.PortScanner()
    scan_result= nm.scan('{}'.format(ip), arguments='-Pn -sS')
    #scan_result = nm.analyse_nmap_xml_scan()
    print(scan_result)
    ports =scan_result['scan'][ip]['tcp']
    for key in scan_result['scan'][ip]['tcp']:
        if scan_result['scan'][ip]['tcp'][key]['state'] == 'open':
            port_list.append(key)
    return port_list