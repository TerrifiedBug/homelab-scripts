# 🐳 Twitch Username Availability Checker (Dockerized)

Check the availability of Twitch usernames on a schedule — complete with optional notifications via **Discord** and **CallMeBot (WhatsApp)**, screenshots, and full Docker support.

---

## 🧰 Features

- ✅ Headless browser check via Playwright
- ✅ Configurable username list
- ✅ Discord + WhatsApp alerts
- ✅ Optional screenshot saving
- ✅ Dockerized with cron scheduling
- ✅ Environment-driven configuration

---

## 🚀 Getting Started

### 🐳 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/homelab-scripts.git
cd homelab-scripts/twitch-username-availability
```

---

### ⚙️ 2. Configure `.env`

Create a `.env` file:

```env
# Comma-separated list of usernames to check
USERNAMES=

# Cron schedule (twice daily example)
CRON_SCHEDULE=0 8,20 * * *

# Notifications
DISCORD_ENABLED=true
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...

CALLMEBOT_ENABLED=true
CALLMEBOT_PHONE=+441234567890
CALLMEBOT_APIKEY=abcdef123456

# Screenshots
SCREENSHOTS_ENABLED=true
```

---

### 📁 3. Files You Should Have

```
.
├── docker-compose.yml
├── Dockerfile
├── .env.template
├── config.json               # Field selectors & UI config
├── twitch_username_check.py  # Main script
├── docker-entrypoint.sh      # Sets up cron
├── requirements.txt      # Requirements
├── screenshots/              # Screenshots saved here (optional)
```

---

### 🐳 4. Build and Run

```bash
docker compose build
docker compose up -d
```

📝 Output is logged to `cron-logs/cron.log`

---

## 🔧 Configuration Files

### 📄 `config.json`

Defines the HTML selectors used to fill/check the site. Already configured for [streampog.com](https://streampog.com):

```json
{
  "site": {
    "url": "https://streampog.com/twitch-username-checker",
    "username_field": "input[name=\"username\"]",
    "submit_button": "button[type=\"submit\"]",
    "result_selector": "#result"
  },
  "screenshots": {
    "enabled": true,
    "path_format": "screenshots/debug_{username}.png"
  }
}
```

---

## 🧪 Test Manually Inside Container

```bash
docker exec -it twitch-checker bash
python3 twitch_username_check.py
```

---

## 📬 Notifications

| Type        | Config                                  |
|-------------|------------------------------------------|
| Discord     | Enable via `.env` and set webhook URL    |
| CallMeBot   | Enable via `.env`, phone number + API key|

---

## 📅 Cron Schedule Examples

| Schedule            | CRON_SCHEDULE              |
|---------------------|----------------------------|
| Every 5 minutes     | `*/5 * * * *`              |
| Twice a day (8 AM + 8 PM) | `0 8,20 * * *`        |
| Every hour          | `0 * * * *`                |

Use [crontab.guru](https://crontab.guru) for easy syntax checks.

---

## 🙌 Credits

Built using:

- [Playwright](https://playwright.dev/)
- [Docker](https://docker.com/)
- [Streampog](https://streampog.com/)
