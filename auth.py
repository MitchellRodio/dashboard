from flask import Blueprint, redirect, request, session, url_for, render_template

import urllib
import requests

from config import CLIENT_ID, AUTHORIZE_URL, MY_URL, CLIENT_SECRET, TOKEN_URL, GUILD_ID
import users
import discord_interaction

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
    print(json)
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
            next_url = session.get("next")
            if next_url:
                return redirect(next_url)
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
            print("Success!")
            user.join(session["access_token"])
            next_url = session.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("main.dashboard")
        else:
            print("Failure!")
            return render_template("enter_key.html", errors=("Key not found.",))
    else:
        return render_template("enter_key.html")