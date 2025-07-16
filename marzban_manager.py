import requests
from config import MARZBAN_URL, MARZBAN_ADMIN_USERNAME, MARZBAN_ADMIN_PASSWORD

def login_admin():
    url = f"{MARZBAN_URL}/api/admin/login"
    payload = {
        "username": MARZBAN_ADMIN_USERNAME,
        "password": MARZBAN_ADMIN_PASSWORD
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise Exception("Failed to get Marzban access token")
    return token

def get_user(token, username):
    url = f"{MARZBAN_URL}/api/user/{username}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def update_user_sni(token, username, new_sni):
    # Assumes the user's inbound config is accessible and modifiable
    url = f"{MARZBAN_URL}/api/user/{username}/inbound"
    headers = {"Authorization": f"Bearer {token}"}
    # Fetch current config
    user_data = get_user(token, username)
    inbound = user_data.get("inbound", {})
    inbound["host"] = new_sni
    inbound["sni"] = new_sni
    response = requests.put(url, json=inbound, headers=headers)
    response.raise_for_status()
    return response.json()

def build_v2ray_link(config, address, host):
    # Compose a VLESS link. Adapt for actual fields.
    uuid = config["uuid"]
    port = config["port"]
    path = config.get("path", "/")
    return (
        f"vless://{uuid}@{address}:{port}"
        f"?encryption=none&security=tls&type=ws&host={host}&path={path}#marzban_user"
    )