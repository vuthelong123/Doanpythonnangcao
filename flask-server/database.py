import mysql.connector
from mysql.connector import pooling
from config import Config

# Khởi tạo connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASS,
    database=Config.DB_DATABASE
)

def get_connection():
    return connection_pool.get_connection()

import decimal

def _map_id(d):
    '''Map id -> _id để tương thích frontend, và chuyển Decimal thành int'''
    if d:
        if 'id' in d:
            d['_id'] = d['id']
        for k, v in d.items():
            if isinstance(v, decimal.Decimal):
                d[k] = int(v)
    return d

def execute_query(query, params=None, fetchone=False, fetchall=False, insert=False):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) # Trả về dictionary
        cursor.execute(query, params)
        
        if insert:
            conn.commit()
            return cursor.lastrowid
        elif fetchone:
            res = cursor.fetchone()
            return _map_id(res)
        elif fetchall:
            res = cursor.fetchall()
            return [_map_id(r) for r in res]
        else:
            conn.commit()
            return cursor.rowcount
    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
