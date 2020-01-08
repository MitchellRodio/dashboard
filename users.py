import psycopg2

import database as db

class User():
    def __init__(self, client_id):
        self.client_id = client_id
    def exists(self):
        conn, cur = db.get_conn()
        cur.execute("SELECT * FROM users WHERE discord_id=%s", (self.client_id,))
        result = cur.fetchone()
        db.put_conn(conn, cursor=cur)
        return not not result# Convert to bool
    def create(self):
        conn, cur = db.get_conn()
        cur.execute("INSERT INTO users discord_id VALUES (%s)", (self.client_id,))
        conn.commit()
        db.put_conn(conn, cursor=cur)


        