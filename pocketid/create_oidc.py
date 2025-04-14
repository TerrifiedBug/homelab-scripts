import requests

# Your domain
domain = "domain.com"

# List of all your services from the Caddyfile
services = [
    "portainer",
    "grafana",
    "nginx",
    "homer",
    "prometheus",
    "wazuh",
    "opensearch",
    "teslamate",
    "pihole",
    "teslamateservice",
    "wordpress",
    "router",
    "investigate",
    "epicgames",
    "n8n",
    "misp",
    "minio",
    "minioapi",
    "api-opensearch",
    "rancher",
    "actualbudget",
    "homepage",
    "2fauth",
    "parcel",
    "homeassistant",
    "httpd",
    "grocy",
    "kibana",
    "authentik",
    "zipline",
    "codeserver",
    "uptime",
    "cyberchef",
    "cv",
    "pdf",
    "it-tools",
    "vw",
    "convertx",
    "neko",
    "resume",
    "changedetection",
    "readme",
    "hoarder",
    "duplicati",
    "glance",
    "cwa",
    "cup",
    "qbittorrent",
    "sonarr",
    "radarr",
    "prowlarr",
    "jellyfin",
    "jellyseer",
    "sabnzbd",
]

# Generate callback URLs for each service
callback_urls = [
    f"https://{service}.{domain}/caddy-security/oauth2/generic/authorization-code-callback"
    for service in services
]

# Your API key
api_key = ""

# API endpoint details
base_url = "https://pocketid.domain.com"  # Replace with your actual Pocket-ID host
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": api_key,
}

# Step 1: Get a list of all clients to find the one named "Pocket ID"
response = requests.get(f"{base_url}/api/oidc/clients", headers=headers)
print(f"Status: {response.status_code}")

try:
    response_data = response.json()

    # Extract clients from the data field
    if "data" in response_data and isinstance(response_data["data"], list):
        clients = response_data["data"]
    else:
        print(f"Unexpected API response structure: {response_data}")
        exit(1)

    # Find the client ID for "Pocket ID"
    client_id = None
    for client in clients:
        if client.get("name") == "Pocket ID":
            client_id = client.get("id")
            break

    if not client_id:
        print("Could not find a client named 'Pocket ID'")
        exit(1)

    print(f"Found client 'Pocket ID' with ID: {client_id}")

    # Step 2: Update the client with the new callback URLs
    payload = {
        "callbackURLs": callback_urls,
        # Include other properties you want to maintain or update
        "name": "Pocket ID",
        "isPublic": False,  # Use the existing value from the API response
        "pkceEnabled": False,  # Use the existing value from the API response
    }

    update_response = requests.put(
        f"{base_url}/api/oidc/clients/{client_id}", headers=headers, json=payload
    )

    print(f"Update Status: {update_response.status_code}")
    print(update_response.text)

except requests.exceptions.JSONDecodeError:
    print("Failed to parse JSON response")
    exit(1)
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
    exit(1)
