"""Script to update callback URLs for OIDC client en masse"""

import requests

DOMAIN = "domain.com"
CLIENT_NAME = "Pocket ID"
API_KEY = ""
BASE_URL = "https://pocketid.domain.com"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY,
}

# List of services you want added to oidc
SERVICES = [
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

CALLBACK_URLS = [
    f"https://{service}.{DOMAIN}/caddy-security/oauth2/generic/authorization-code-callback"
    for service in SERVICES
]


def main():
    """Main function to get and update client information."""
    # Step 1: Get a list of all clients to find the one named in CLIENT_NAME
    response = requests.get(f"{BASE_URL}/api/oidc/clients", headers=HEADERS, timeout=60)
    print(f"Status: {response.status_code}")

    try:
        response_data = response.json()

        if "data" in response_data and isinstance(response_data["data"], list):
            clients = response_data["data"]
        else:
            print(f"Unexpected API response structure: {response_data}")
            exit(1)

        # Find the client ID for the specified client name
        client_id = None
        for client in clients:
            if client.get("name") == CLIENT_NAME:
                client_id = client.get("id")
                break

        if not client_id:
            print(f"Could not find a client named '{CLIENT_NAME}'")
            exit(1)

        print(f"Found client '{CLIENT_NAME}' with ID: {client_id}")

        payload = {
            "callbackURLs": CALLBACK_URLS,
            "name": CLIENT_NAME,
            "isPublic": False,
            "pkceEnabled": False,
        }

        update_response = requests.put(
            f"{BASE_URL}/api/oidc/clients/{client_id}",
            headers=HEADERS,
            json=payload,
            timeout=60,
        )

        print(f"Update Status: {update_response.status_code}")
        print(update_response.text)

    except requests.exceptions.JSONDecodeError:
        print("Failed to parse JSON response")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
