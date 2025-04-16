"""Script to update callback URLs for OIDC client en masse. OIDC Needs to exist before hand"""

import requests

DOMAIN = "domain.com"
CLIENT_NAME = "Pocket ID"
API_KEY = ""
POCKETID_BASE_URL = "https://pocketid.domain.com"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-API-KEY": API_KEY,
}


def load_services():
    """Load services from services.txt file."""
    try:
        with open("services.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Error: services.txt file not found")
        exit(1)


SERVICES = load_services()

CALLBACK_URLS = [
    f"https://{service}.{DOMAIN}/caddy-security/oauth2/generic/authorization-code-callback"
    for service in SERVICES
]


def main():
    """Main function to get and update client information."""
    response = requests.get(
        f"{POCKETID_BASE_URL}/api/oidc/clients", headers=HEADERS, timeout=60
    )
    print(f"Status: {response.status_code}")

    try:
        response_data = response.json()

        if "data" in response_data and isinstance(response_data["data"], list):
            clients = response_data["data"]
        else:
            print(f"Unexpected API response structure: {response_data}")
            exit(1)

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
            f"{POCKETID_BASE_URL}/api/oidc/clients/{client_id}",
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
