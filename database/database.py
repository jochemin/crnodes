import os.path
import sqlite3
from sqlite3 import Error
import datetime

def check_database_exist():
    if os.path.isfile('./database/crnodes.db'):
        return True
    else:
        return False
    
def create_database():
    # Connect to or create the database
    conn = sqlite3.connect('./database/crnodes.db')

    # Create a cursor object
    c = conn.cursor()

    # Create the nodes table
    c.execute('''
        CREATE TABLE nodes (
            added DATE,
            address TEXT,
            address_type TEXT,
            last_scan DATE,
            open_ports TEXT,
            vulnerabilities TEXT,
            notes TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_new_node(address, address_type, port):
    conn = sqlite3.connect('./database/crnodes.db')
    c = conn.cursor()

    now = datetime.datetime.now()
    added = now.strftime('%d/%m/%Y %H:%M:%S')
    
    values = (
        added,
        address,
        address_type,
        port
    )
    c.execute('''
        INSERT INTO nodes (
            added, address, address_type, open_ports
        ) VALUES (?, ?, ?, ?)
    ''', values)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()