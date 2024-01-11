import requests

## All external data logic

def bitnodes_reachable_ip_list():
    ## https://bitnodes.io/api/#list-nodes
    url='https://bitnodes.io/api/v1/snapshots/latest/'
    r = requests.get(url, 
                 headers={'Accept': 'application/json'})
    return r.json()['nodes']

def bitnode_dict():
    nodict={}
    for node in bitnodes_reachable_ip_list():
        node_address = node.rsplit(':',1)[0]
        node_port = node.rsplit(':',1)[1]
        nodict[node_address] = node_port
    return nodict

