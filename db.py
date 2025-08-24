import os
import mysql.connector
from mysql.connector import pooling

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "Salopekselo2"),
    "database": os.getenv("DB_NAME", "SkladisteDB"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

pool = pooling.MySQLConnectionPool(
    pool_name="skladiste_pool",
    pool_size=5,
    autocommit=False,
    **DB_CONFIG
)

def get_conn():
    return pool.get_connection()