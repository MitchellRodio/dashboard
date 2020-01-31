from flask import session, request, url_for, redirect

import functools
import time
import datetime
import string
import random

from config import GUILD_ID
import database as db
import discord_interaction

class Membership():
    def __init__(self, discord_id, created_at, duration):
        self.discord_id = discord_id
        self.created_at = created_at
        self.duration = duration
        self.duration_display = int(self.duration // 86400) # Converting from seconds to days
        self.expires_in = (self.duration + self.created_at) - time.time()
        self.expires_in_display = int(self.expires_in // 86400)
    def is_active(self):
        if self.duration == 0:
            return False
        current_time = time.time()
        return current_time - self.created_at < self.duration

class DisplayUser():
    def __init__(self, discord_id, name, avatar_url):
        self.discord_id = discord_id
        self.name = name
        self.avatar_url = avatar_url
    @classmethod
    def from_session(cls):
        discord_data = session.get("discord_data")
        if discord_data:
            return cls(discord_data.get("id"), discord_data.get("username")+"#"+discord_data.get("discriminator"), discord_data.get("avatar_url"))

class User():
    def __init__(self, discord_id):
        self.discord_id = discord_id
        self.membership = self.get_membership()
    def get_membership(self):
        conn, cur = db.get_conn()
        cur.execute("SELECT started_at, duration FROM memberships WHERE discord_id=%s", (self.discord_id,))
        result = cur.fetchone()
        db.put_conn(conn, cursor=cur)
        if result:
            return Membership(self.discord_id, result[0], result[1])
        else:
            return Membership(self.discord_id, 0, 0)
    def join(self, access_token):
        discord_interaction.join_user(access_token, GUILD_ID, self.discord_id)
    def kick(self):
        discord_interaction.kick_user(GUILD_ID, self.discord_id)
    def create_membership(self, key):
        conn, cur = db.get_conn()
        cur.execute("SELECT duration FROM keys WHERE key=%s", (key,))
        result = cur.fetchone()
        membership = False
        if result:
            cur.execute("DELETE FROM keys WHERE key=%s", (key,))
            if self.membership and self.membership.duration != 0:
                cur.execute("UPDATE memberships SET started=%s, duration=%s WHERE discord_id=%s", (int(time.time()), result[0], self.discord_id))
            else:
                cur.execute("INSERT INTO memberships (discord_id, started_at, duration) VALUES (%s, %s, %s)", (self.discord_id, int(time.time()), result[0]))   
            conn.commit()
            self.get_membership()
            membership = True
        db.put_conn(conn, cursor=cur)
        return membership
    def exists(self):
        conn, cur = db.get_conn()
        cur.execute("SELECT * FROM users WHERE discord_id=%s", (self.discord_id,))
        result = cur.fetchone()
        db.put_conn(conn, cursor=cur)
        return not not result# Convert to bool
    def create(self):
        conn, cur = db.get_conn()
        cur.execute("INSERT INTO users (discord_id) VALUES (%s)", (self.discord_id,))
        conn.commit()
        db.put_conn(conn, cursor=cur)
    def get_login_key(self):
        conn, cur = db.get_conn()
        cur.execute("SELECT key FROM login_keys WHERE discord_id=%s", (self.discord_id,))
        result = cur.fetchone()
        db.put_conn(conn, cursor=cur)
        if result:
            return result[0]
    def set_login_key(self, length=16):
        key = "".join(random.choice(tuple(string.digits+string.ascii_letters)) for _ in range(length))
        conn, cur = db.get_conn()
        if self.get_login_key():
            cur.execute("UPDATE login_keys SET key=%s WHERE discord_id=%s", (key, self.discord_id))
        else:
            cur.execute("INSERT INTO login_keys (discord_id, key) VALUES (%s, %s)", (self.discord_id, key))
        conn.commit()
        db.put_conn(conn, cursor=cur)
        return key


def logged_in(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if user:
            return func(user, *args, **kwargs)
        else:
            return redirect(url_for("auth.login"))
    return decorated_function

def has_membership(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):# Maybe could make this take user as an argument
        user = get_user()
        if not user:
            return redirect(url_for("auth.login"))
        if user.membership.is_active():
            return func(*args, **kwargs)
        else:
            return redirect(url_for("auth.enter_key"))
    return decorated_function

def get_user():
    if session.get("logged_in") == True:
        return User(session["discord_data"]["id"])
    else:
        return None