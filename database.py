import psycopg2
import psycopg2.pool
import os

# If having trouble writing BLOB (BYTEA) data into Postgres try encoding it into a string with base64 and then store as text

connection_pool = psycopg2.pool.ThreadedConnectionPool(5, 20, os.environ["DATABASE"])
print(os.environ)
print(os.environ["DATABASE"])
def get_conn(cursor=True):
    conn = connection_pool.getconn()
    if cursor:
        return conn, conn.cursor()
    else:
        return conn

def put_conn(conn, cursor=None):
    if cursor:
        cursor.close()
    connection_pool.putconn(conn)