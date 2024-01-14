import os.path
import sqlite3
from sqlite3 import Error
import datetime

def database_connect():  #https://phiresky.github.io/blog/2020/sqlite-performance-tuning/
    conn = sqlite3.connect('./database/crnodes.db')
    conn.execute('pragma journal_mode=wal')
    conn.execute('pragma synchronous = normal')
    conn.execute('pragma temp_store = memory')
    conn.execute('pragma mmap_size = 30000000000')
    return conn

def check_database_exist():
    if os.path.isfile('./database/crnodes.db'):
        return True
    else:
        return False
    
def create_database():
    # Connect to or create the database
    with database_connect() as conn:

        # Create a cursor object
        c = conn.cursor()

        # Create the nodes table
        c.execute('''
            CREATE TABLE nodes (
                added DATE,
                address TEXT UNIQUE,
                address_type TEXT,
                bitcoin_port TEXT,
                last_scan DATE,
                user_agent TEXT,
                open_ports TEXT,
                port_scan_date DATE,
                online_score INTEGER,
                vulnerabilities TEXT,
                notes TEXT
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()

def insert_new_node(address, address_type, port):
    with database_connect() as conn:
        c = conn.cursor()

        now = datetime.datetime.now()
        added = now.strftime('%d/%m/%Y %H:%M:%S')
        
        values = (
            added,
            address,
            address_type,
            port,
            100
        )
        try:
            c.execute('''
                INSERT INTO nodes (
                    added, address, address_type, bitcoin_port, online_score
                ) VALUES (?, ?, ?, ?, ?)
            ''', values)
            # Commit the changes and close the connection
            conn.commit()
        except Exception:
            return "Error"

def all_nodes():
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT address, bitcoin_port, online_score FROM nodes WHERE last_scan IS NULL")
        rows = c.fetchall()
        return rows

def no_user_agent():
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT address, bitcoin_port FROM nodes WHERE user_agent IS NULL")
        rows = c.fetchall()
        return rows

def no_scan_date():
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT address FROM nodes WHERE last_scan IS NULL")
        rows = c.fetchall()
        return rows

def ssh_open_nodes():
    port_query = "%"+"22"+"%"
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("SELECT address from nodes where open_ports LIKE '%{}%'".format("22"))
        rows = c.fetchall()
        return rows

def add_user_agent(address, user_agent):
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("UPDATE nodes SET user_agent=? WHERE address=?", (user_agent, address))
        conn.commit()

def add_open_ports(address, port_list):
    now = datetime.datetime.now()
    scan_port_date = now.strftime('%d/%m/%Y %H:%M:%S')
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("UPDATE nodes SET open_ports=?, port_scan_date=? WHERE address=?", (port_list, scan_port_date, address))
        conn.commit()

def update_online_score(address, online_score):
    with database_connect() as conn:
        c = conn.cursor()
        c.execute("UPDATE nodes SET online_score=? WHERE address=?", (online_score, address))
        conn.commit()
    
def delete_node(address):
    with database_connect() as conn:
        c= conn.cursor()
        c.execute("DELETE FROM nodes WHERE address = ?",(address))
        conn.commit()