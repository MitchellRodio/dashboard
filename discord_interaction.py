from flask import url_for
import requests

from config import TOKEN

def get_me(access_token):
    url = "https://discordapp.com/api/v6/users/@me"# User info
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    data = r.json()
    if data:
        client_id = int(data.get("id"))
        data["id"] = client_id
        avatar_hash =  data.get("avatar")
        if avatar_hash:
            image_format = "png"
            size = 256
            data["avatar_url"] = f"https://cdn.discordapp.com/avatars/{client_id}/{avatar_hash}.{image_format}?size={size}"
        else:
            data["avatar_url"] = url_for("static", filename="images/default_avatar.png")
    return data

def join_user(access_token, guild_id, user_id):
    url = f"https://discordapp.com/api/v6/guilds/{guild_id}/members/{user_id}"
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
    r = requests.put(url, json={"access_token": access_token}, headers=headers)
    return r.status_code

def kick_user(guild_id, user_id):
    url = f"https://discordapp.com/api/v6/guilds/{guild_id}/members/{user_id}"
    headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
    r = requests.delete(url, headers=headers)
    return r.status_code
