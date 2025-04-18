"""Twitch username checker with notifications and dynamic config."""

import json
import os

import requests
from playwright.sync_api import sync_playwright

CONFIG_PATH = "config.json"
NOTIFICATIONS_PATH = "notifications.json"
USERNAMES_PATH = "usernames.txt"


def load_json(file_path):
    """Load JSON from a file."""
    if not os.path.exists(file_path):
        print(f"[!] File not found: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def send_discord_notification(webhook_url, message):
    """Send a message to a Discord webhook."""
    try:
        requests.post(webhook_url, json={"content": message}, timeout=10)
        print("[🔔] Discord notification sent.")
    except requests.RequestException as error:
        print(f"[!] Discord notification failed: {error}")


def send_callmebot_sms(phone_number, api_key, message):
    """Send a message via CallMeBot."""
    try:
        url = (
            f"https://api.callmebot.com/whatsapp.php?"
            f"phone={phone_number}&apikey={api_key}&text={requests.utils.quote(message)}"
        )
        requests.get(url, timeout=10)
        print("[📱] CallMeBot notification sent.")
    except requests.RequestException as error:
        print(f"[!] CallMeBot notification failed: {error}")


def send_notifications(config, message):
    """Dispatch notifications based on enabled services."""
    if config.get("discord", {}).get("enabled"):
        send_discord_notification(config["discord"]["webhook_url"], message)
    if config.get("callmebot", {}).get("enabled"):
        send_callmebot_sms(
            config["callmebot"]["phone_number"], config["callmebot"]["api_key"], message
        )


def check_username_availability(username, site_conf, screenshot_conf):
    """Check if a Twitch username is available."""
    print(f"\n[*] Checking username: {username}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(site_conf["url"])

        page.fill(site_conf["username_field"], username)
        page.click(site_conf["submit_button"])
        page.wait_for_timeout(1500)  # Wait 1.5 seconds to let the result load

        try:
            page.wait_for_selector(site_conf["result_selector"], timeout=10000)
            result_elem = page.query_selector(site_conf["result_selector"])

            if not result_elem:
                print("[!] No result element found.")
                return None, False

            result_text = result_elem.inner_text().strip()
            result_classes = result_elem.get_attribute("class") or ""

            print(f"[DEBUG] Result text: {result_text}")
            print(f"[DEBUG] Result classes: {result_classes}")

            is_available = "alert-success" in result_classes

        except Exception as error:
            print(f"[!] Error while checking username: {error}")
            result_text = None
            is_available = False

        if screenshot_conf.get("enabled", False):
            screenshot_path = screenshot_conf["path_format"].format(username=username)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[*] Screenshot saved: {screenshot_path}")

        browser.close()
        return result_text, is_available


def load_usernames():
    """Load usernames from a static file."""
    if not os.path.exists(USERNAMES_PATH):
        print(f"[!] Usernames file not found: {USERNAMES_PATH}")
        return []
    with open(USERNAMES_PATH, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def main():
    """Main script execution."""
    config = load_json(CONFIG_PATH)
    notifications = load_json(NOTIFICATIONS_PATH)
    site_conf = config["site"]
    screenshot_conf = config.get("screenshots", {})
    usernames = load_usernames()

    if not usernames:
        print("[!] No usernames to check.")
        return

    for username in usernames:
        result_text, is_available = check_username_availability(
            username, site_conf, screenshot_conf
        )

        if result_text:
            print(f"[✔️] {username}: {result_text}")
            if is_available:
                msg = f'Username "{username}" is available on Twitch.'
                send_notifications(notifications, msg)
        else:
            print(f"[❌] {username}: No result found.")


if __name__ == "__main__":
    main()
