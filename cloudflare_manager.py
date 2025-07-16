import random
import string
import requests
from config import CLOUDFLARE_API_TOKEN, CLOUDFLARE_ZONE_ID, CLOUDFLARE_DOMAIN, MAIN_SERVER_IP

CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"

def generate_subdomain(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_subdomain(subdomain):
    url = f"{CLOUDFLARE_API_BASE}/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": f"{subdomain}.{CLOUDFLARE_DOMAIN}",
        "content": MAIN_SERVER_IP,
        "proxied": True
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise Exception(f"Cloudflare API error: {data}")
    return f"{subdomain}.{CLOUDFLARE_DOMAIN}"

def get_random_clean_ip():
    with open("clean_ips.txt", "r") as f:
        ips = [line.strip() for line in f if line.strip()]
    if not ips:
        raise Exception("No clean IPs available.")
    return random.choice(ips)