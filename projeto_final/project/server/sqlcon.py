import os
import sqlite3
from config import *

def initializeDatabase():
    try:
        if not(os.path.exists(STORAGE_DB)):
            connection = sqlite3.connect(STORAGE_DB)
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE users (
                    username TEXT NOT NULL PRIMARY KEY,
                    password TEXT NOT NULL,
                    owimages TEXT)
            """)
            cursor.execute("""
                CREATE TABLE tokens (
                    token TEXT NOT NULL PRIMARY KEY,
                    expiry INTEGER NOT NULL,
                    username TEXT NOT NULL)
            """)
            cursor.execute("""
                CREATE TABLE images (
                    identifier INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection INTEGER NOT NULL,
                    extension TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    history TEXT,
                    owner TEXT)
            """)
            cursor.execute("""
                CREATE TABLE collections (
                    identifier INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner TEXT NOT NULL,
                    name TEXT NOT NULL)
            """)
            connection.commit()
            connection.close()
    except sqlite3.Error as error:
        raise Exception("Error connecting to the database: ", error)

def selector(query, tupledata=None):
    connection = sqlite3.connect(STORAGE_DB)
    cursor = connection.cursor()
    cursor.execute(query, tupledata)
    data =  cursor.fetchall()
    connection.close()
    return data

def executor(query, tupledata=None):
    connection = sqlite3.connect(STORAGE_DB)
    cursor = connection.cursor()
    cursor.execute(query, tupledata)
    connection.commit()
    connection.close()