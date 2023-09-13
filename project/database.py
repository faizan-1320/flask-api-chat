# db.py
import os
import mysql.connector
from flask import g

def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                user=os.environ['MYSQL_USER'],
                password=os.environ['MYSQL_PASSWORD'],
                host=os.environ['MYSQL_HOST'],
                database=os.environ['MYSQL_DB']
            )
        except Exception as e:
            return None, str(e)
    return g.db

def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()
