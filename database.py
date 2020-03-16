import psycopg2
import psycopg2.pool
import os

# If having trouble writing BLOB (BYTEA) data into Postgres try encoding it into a string with base64 and then store as text

connection_pool = psycopg2.pool.ThreadedConnectionPool(5, 20, user="postgres://hyazuvvffogsks:b5b47ad5d42f5e667269eb712a894ff66fa652014adbe8ba2481ccaca33ed547@ec2-23-22-156-110.compute-1.amazonaws.com:5432/df2mi901e5abfr", password="odesha", dbname="odesha")

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