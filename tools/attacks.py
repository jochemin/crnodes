import http.client

def port_80_information(ip):
    connection = http.client.HTTPConnection(ip, 80, timeout=10)
    connection.request("GET", "/")
    response = connection.getresponse()
    headers = response.getheaders()
    print(response.getheaders())

port_80_information('62.159.33.3')