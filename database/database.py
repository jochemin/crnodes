import os.path
import sqlite3
from sqlite3 import Error

def check_database_exist():
    if os.path.isfile('./crnodes.db'):
        return True
    else:
        return False