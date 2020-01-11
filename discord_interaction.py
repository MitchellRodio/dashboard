import requests

from config import TOKEN

def get_me(access_token):
    url = "https://discordapp.com/api/v6/users/@me"# User info
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    return_json = r.json()
    if return_json:
        return_json["id"] = int(return_json["id"])
    return return_json

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
