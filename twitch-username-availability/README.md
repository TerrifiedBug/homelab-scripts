🐳 Twitch Username Availability Checker (Dockerized)
Check the availability of Twitch usernames on a schedule — complete with optional notifications via Discord and CallMeBot (WhatsApp), screenshots, and full Docker support.

🧰 Features
✅ Headless browser check via Playwright

✅ Configurable username list (usernames.txt)

✅ Discord + WhatsApp alerts

✅ Optional screenshot saving

✅ Dockerized with cron scheduling

✅ Environment-driven configuration

🚀 Getting Started
🐳 1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/<your-username>/homelab-scripts.git
cd homelab-scripts/twitch-username-availability
⚙️ 2. Configure .env
Create a .env file:

env
Copy
Edit
# Comma-separated list of usernames to check (optional if using usernames.txt)
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
📁 3. Files You Should Have
bash
Copy
Edit
.
├── docker-compose.yml
├── Dockerfile
├── .env
├── config.json               # Field selectors & UI config
├── notifications.json        # (Optional if using .env)
├── usernames.txt             # List of usernames to check
├── twitch_username_check.py  # Main script
├── docker-entrypoint.sh      # Sets up cron
├── screenshots/              # Screenshots saved here (optional)
🐳 4. Build and Run
bash
Copy
Edit
docker compose build
docker compose up -d
📝 Output is logged to cron-logs/cron.log

🔧 Configuration Files
📄 usernames.txt
List one username per line:

nginx
Copy
Edit
itsfruity
xqc
exampleuser123
📄 config.json
Defines the HTML selectors used to fill/check the site. Already configured for streampog.com:

json
Copy
Edit
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
🧪 Test Manually Inside Container
bash
Copy
Edit
docker exec -it twitch-checker bash
python3 twitch_username_check.py
📬 Notifications
Type	Config
Discord	Enable via .env and set webhook URL
CallMeBot	Enable via .env, phone number + API key
📅 Cron Schedule Examples
Schedule	CRON_SCHEDULE
Every 5 minutes	*/5 * * * *
Twice a day (8 AM + 8 PM)	0 8,20 * * *
Every hour	0 * * * *
Use crontab.guru for easy syntax checks.

🔐 Security Notes
Avoid committing secrets to Git!

Use .env or secrets manager for sensitive API keys

Add .env to your .gitignore

🙌 Credits
Built using:

Playwright

Docker

Streampog
