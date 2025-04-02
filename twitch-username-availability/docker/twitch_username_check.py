"""Twitch username checker using environment-based config."""

import json
import os

import requests
from playwright.sync_api import sync_playwright


def load_config():
    """Load config json."""
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)


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


def send_notifications(message):
    """Send notifications based on environment config."""
    if os.getenv("DISCORD_ENABLED", "false").lower() == "true":
        send_discord_notification(os.getenv("DISCORD_WEBHOOK"), message)
    if os.getenv("CALLMEBOT_ENABLED", "false").lower() == "true":
        send_callmebot_sms(
            os.getenv("CALLMEBOT_PHONE"),
            os.getenv("CALLMEBOT_APIKEY"),
            message,
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
            is_available = "alert-success" in result_classes

        except Exception as error:
            print(f"[!] Error while checking username: {error}")
            result_text = None
            is_available = False

        # Check env override, fallback to config.json
        screenshot_enabled = (
            os.getenv(
                "SCREENSHOTS_ENABLED", str(screenshot_conf.get("enabled", False))
            ).lower()
            == "true"
        )

        if screenshot_enabled:
            screenshot_path = screenshot_conf["path_format"].format(username=username)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"[*] Screenshot saved: {screenshot_path}")

        browser.close()
        return result_text, is_available


def main():
    """Main entry point."""
    config = load_config()
    site_conf = config["site"]
    screenshot_conf = config.get("screenshots", {})

    usernames_raw = os.getenv("USERNAMES", "")
    usernames = [u.strip() for u in usernames_raw.split(",") if u.strip()]

    if not usernames:
        print("[!] No usernames provided via environment.")
        return

    for username in usernames:
        result_text, is_available = check_username_availability(
            username, site_conf, screenshot_conf
        )

        if result_text:
            print(f"[✔️] {username}: {result_text}")
            if is_available:
                message = f'Username "{username}" is available on Twitch.'
                send_notifications(message)
        else:
            print(f"[❌] {username}: No result found.")


if __name__ == "__main__":
    main()
