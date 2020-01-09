from flask import session, request, url_for, redirect

import functools

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

def logged_in(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if user:
            return func(user, *args, **kwargs)
        else:
            session["next"] = request.url_rule.rule
            return redirect(url_for("auth.login"))
    return decorated_function

def get_user():
    if session.get("logged_in") == True:
        return User(session["discord_data"]["id"])
    else:
        return None