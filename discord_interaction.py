import requests

def get_me(access_token):
    url = "https://discordapp.com/api/v6/users/@me"# User info
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    return_json = r.json()
    if return_json:
        return_json["id"] = int(return_json["id"])
    return return_json