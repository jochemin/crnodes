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
            bitcoin_port TEXT,
            last_scan DATE,
            user_agent TEXT,
            open_ports TEXT,
            port_scan_date DATE,
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
            added, address, address_type, bitcoin_port
        ) VALUES (?, ?, ?, ?)
    ''', values)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def no_user_agent():
    conn = sqlite3.connect('./database/crnodes.db')
    c = conn.cursor()
    c.execute("SELECT address, bitcoin_port FROM nodes WHERE user_agent IS NULL")
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def no_scan_date():
    conn = sqlite3.connect('./database/crnodes.db')
    c = conn.cursor()
    c.execute("SELECT address FROM nodes WHERE last_scan IS NULL")
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

def add_user_agent(address, user_agent):
    conn = sqlite3.connect('./database/crnodes.db')
    c = conn.cursor()
    c.execute("UPDATE nodes SET user_agent=? WHERE address=?", (user_agent, address))
    conn.commit()
    c.close()
    conn.close()

def add_open_ports(address, port_list):
    now = datetime.datetime.now()
    scan_port_date = now.strftime('%d/%m/%Y %H:%M:%S')
    conn = sqlite3.connect('./database/crnodes.db')
    c = conn.cursor()
    c.execute("UPDATE nodes SET open_ports=?, port_scan_date=? WHERE address=?", (port_list, scan_port_date, address))
    conn.commit()
    c.close()
    conn.close()