"""Script to export all Portainer stacks into a local structured directory"""

import argparse
import json  # for pretty-printing debug output
import os
from getpass import getpass

import requests

PORTAINER_URL = "redacted"
OUTPUT_DIR = "homelab-stacks"


def login(username, password):
    """Function to get portainer jwt"""
    print("[+] Authenticating to Portainer...")
    resp = requests.post(
        f"{PORTAINER_URL}/api/auth",
        json={"Username": username, "Password": password},
        verify=False,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["jwt"]


def get_stacks(token):
    """Fetch all stacks"""
    print("[+] Fetching stacks...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{PORTAINER_URL}/api/stacks", headers=headers, verify=False, timeout=60
    )
    resp.raise_for_status()
    return resp.json()


def get_stack_detail(token, stack_id):
    """Loop over all stacks to get stack details"""

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{PORTAINER_URL}/api/stacks/{stack_id}",
        headers=headers,
        verify=False,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def get_stack_file(token, stack_id):
    """Get each stack yaml file"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{PORTAINER_URL}/api/stacks/{stack_id}/file",
        headers=headers,
        verify=False,
        timeout=60,
    )
    if resp.status_code == 200:
        return resp.text
    else:
        print(f"[!] Failed to fetch /file for stack {stack_id}: {resp.status_code}")
        return None


def save_stack(stack_name, stack_content):
    """Save each stack locally to its respective directory"""
    safe_name = stack_name.replace(" ", "_")
    path = os.path.join(OUTPUT_DIR, safe_name)
    os.makedirs(path, exist_ok=True)

    print(f"[DEBUG] Saving to file for {stack_name} (type={type(stack_content)}):")
    print(stack_content[:200])  # preview first 200 characters

    compose_file_path = os.path.join(path, "docker-compose.yml")
    with open(compose_file_path, "w", encoding="utf-8") as f:
        f.write(stack_content)

    print(f"[+] Saved {stack_name} to {compose_file_path}")


def save_env_file(stack_name, env_vars):
    """If Stack also contains an existing .env file, save this as stack.env in the same directory"""
    if not env_vars:
        return  # No environment variables to save

    safe_name = stack_name.replace(" ", "_")
    path = os.path.join(OUTPUT_DIR, safe_name)
    os.makedirs(path, exist_ok=True)

    env_path = os.path.join(path, "stack.env")
    with open(env_path, "w", encoding="utf-8") as f:
        for item in env_vars:
            name = item.get("name")
            value = item.get("value", "")
            if name:
                f.write(f"{name}={value}\n")

    print(f"[+] Saved stack.env file for {stack_name} to {env_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Export Portainer stacks to Docker Compose files."
    )
    parser.add_argument("-u", "--username", required=True, help="Portainer username")
    parser.add_argument(
        "-p",
        "--password",
        help="Portainer password (if not provided, will prompt securely)",
    )
    args = parser.parse_args()

    password = args.password or getpass("Portainer Password: ")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    token = login(args.username, password)
    stacks = get_stacks(token)

    print(f"[DEBUG] Retrieved {len(stacks)} stack(s)")
    for stack in stacks:
        print(f"\n[DEBUG] Stack Summary: {stack['Name']} (ID: {stack['Id']})")

        details = get_stack_detail(token, stack["Id"])
        print(f"[DEBUG] Stack Detail JSON:\n{json.dumps(details, indent=2)}")

        env_vars = details.get("Env", [])
        save_env_file(stack["Name"], env_vars)

        # Try to get the actual file from /api/stacks/{id}/file
        stack_content = get_stack_file(token, stack["Id"])

        # Check if content is accidentally JSON-wrapped
        try:
            parsed = json.loads(stack_content)
            if isinstance(parsed, dict) and "StackFileContent" in parsed:
                print(
                    f"[DEBUG] Extracting YAML from JSON-wrapped response for {stack['Name']}"
                )
                stack_content = parsed["StackFileContent"]
        except (json.JSONDecodeError, TypeError):
            pass  # It's raw YAML

        if stack_content:
            save_stack(stack["Name"], stack_content)
        else:
            print(f"[!] Skipping {stack['Name']} (no file content returned)")


if __name__ == "__main__":
    main()
