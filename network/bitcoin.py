import socket
import time
import random
import struct
import hashlib
import binascii

def create_sub_version():
    sub_version = "/Satoshi:26.0.0/"
    return b'\x0F' + sub_version.encode()

# Binary encode the network addresses
def create_network_address(ip_address, port):
    network_address = struct.pack('>8s16sH', b'\x01', 
        bytearray.fromhex("00000000000000000000ffff") + socket.inet_aton(ip_address), port)
    return(network_address)

# Create the TCP request object
def create_message(magic, command, payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return(struct.pack('L12sL4s', magic, command.encode(), len(payload), checksum) + payload)

# Create the "version" request payload
def create_payload_version(peer_ip_address,port):
    version = 70001
    services = 1
    timestamp = int(time.time())
    addr_local = create_network_address("193.107.86.49", 8333)
    addr_peer = create_network_address(peer_ip_address, port)
    nonce = random.getrandbits(64)
    start_height = 0
    payload = struct.pack('<LQQ26s26sQ16sL', version, services, timestamp, addr_peer,
                          addr_local, nonce, create_sub_version(), start_height)
    return(payload)

def print_response(command, request_data, response_data):
    print("")
    print("Command: " + command)
    print("Request:")
    print(request_data)
    print("Response:")
    print(binascii.hexlify(response_data))
    print(response_data.decode('latin1'))

def get_bitcoin_version(ip, port):
    magic_value = 0xd9b4bef9
    peer_ip_address = ip
    peer_tcp_port = port
    buffer_size = 1024

    # Create Request Objects
    version_payload = create_payload_version(peer_ip_address, port)
    version_message = create_message(magic_value, 'version', version_payload)

    # Establish TCP Connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_ip_address, peer_tcp_port))

    # Send message "version"
    s.send(version_message)
    response_data = s.recv(buffer_size)
    print_response("version", version_message, response_data)

    # Close the TCP connection
    s.close()

get_bitcoin_version("54.80.54.71",8333)