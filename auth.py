from flask import Blueprint, redirect, request, session, url_for, render_template, jsonify
import urllib
import requests

import time

from config import CLIENT_ID, AUTHORIZE_URL, MY_URL, CLIENT_SECRET, TOKEN_URL, GUILD_ID
import users
import discord_interaction
import database as db

scopes = "identify email guilds.join"

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    params = {"response_type": "code", "client_id": CLIENT_ID, "scope": scopes, "redirect_uri": f"{MY_URL}/token"}
    params_string = urllib.parse.urlencode(params)
    url = f"{AUTHORIZE_URL}?{params_string}"
    return redirect(url)

@auth.route("/token")
def token():
    code = request.args.get("code")
    data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "authorization_code", "code": code, "scope": scopes, "redirect_uri": f"{MY_URL}/token"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(TOKEN_URL, data=data, headers=headers)
    json = r.json()
    if "access_token" in json:
        session["discord_data"] = discord_interaction.get_me(json["access_token"])
        session["logged_in"] = True
        session["access_token"] = json["access_token"]
        discord_id = session["discord_data"]["id"]
        user = users.User(discord_id)
        if not user.exists():
            user.create()
        if user.membership.is_active():
            discord_interaction.join_user(json["access_token"], GUILD_ID, user.discord_id)
            return redirect(url_for("main.dashboard"))
        else:
            discord_interaction.kick_user(GUILD_ID, user.discord_id)
            return redirect(url_for("auth.enter_key"))
    else:
        session["logged_in"] = False
        session["access_token"] = None
        return redirect(url_for("main.index"))

@auth.route("/key", methods=["GET", "POST"])
@users.logged_in
def enter_key(user):
    if request.method == "POST":
        key = request.form.get("key")
        success = user.create_membership(key)
        if success:
            user.join(session["access_token"])
            return redirect(url_for("main.dashboard"))
        else:
            return render_template("enter_key.html", errors=("Key not found.",))
    else:
        return render_template("enter_key.html")

@auth.route("/app/auth")
def app_auth():
    key = request.args.get("key")
    response = {"login": False}
    if key:
        conn, cur = db.get_conn()
        cur.execute("SELECT discord_id FROM login_keys WHERE key=%s", (key,))
        result = cur.fetchone()
        if result:
            cur.execute("SELECT address, last_login FROM ip_address_logins WHERE discord_id=%s", (result[0],))
            result1 = cur.fetchone()
            current_time = time.time()
            if result1:
                if result1[0] != request.remote_addr and result1[1] - current_time < 10800:# 10800 = 3hrs
                    response["reason"] = "Cannot use multiple IP addresses in quick succession."
                else:
                    response["login"] = True
                    response["discord_id"] = result[0]
                cur.execute("UPDATE ip_address_logins SET address=%s, last_login=%s, logins=logins+1 WHERE discord_id=%s", (request.remote_addr, current_time, result[0]))
            else:
                response["login"] = True
                response["discord_id"] = result[0]
                cur.execute("INSERT INTO ip_address_logins VALUES (%s, %s, 0, %s)", (result[0], request.remote_addr, current_time))
        else:
            response["reason"] = "Invalid key."
        conn.commit()
        db.put_conn(conn, cursor=cur)

    return jsonify(response)