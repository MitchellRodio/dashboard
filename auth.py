from flask import Blueprint, redirect, request, session, url_for

import urllib
import requests

from config import CLIENT_ID, AUTHORIZE_URL, MY_URL, CLIENT_SECRET, TOKEN_URL
import users
import discord_interaction

scopes = "identify email guilds.join"

auth = Blueprint("blueprint", __name__)

@auth.route("/login")
def login():
    params = {"response_type": "code", "client_id": CLIENT_ID, "scope": scopes, "redirect_uri": f"{MY_URL}/token"}
    params_string = urllib.parse.urlencode(params)
    url = f"{AUTHORIZE_URL}?{params_string}"
    return redirect(url)

@auth.route("/token")
def token():
    code = request.args.get("code")
    data = {"client_id" :CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "authorization_code", "code": code, "scope": scopes, "redirect_uri": f"{MY_URL}/token"}
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
        next_url = session.get("next")
        if next_url:
            return redirect(next_url)
    else:
        session["logged_in"] = False
        session["access_token"] = None
    return redirect(url_for("main.index"))