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
        info = scan_result['scan'][ip]['tcp'][port]['script']['bitcoin-info']
        return(info.split('User Agent: ',1)[1])
    except KeyError:
        return "Error"

test = get_node_version('35.203.15.57', 8333)
print(test)
#result = (test['scan'])
#for key, value in result.items():
#    print(key)