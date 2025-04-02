FROM python:3.12-slim

WORKDIR /app

# Install OS packages: cron + curl for playwright + cron logging
RUN apt-get update && \
    apt-get install -y curl cron && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip + playwright
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install-deps && \
    playwright install

# Copy the app code
COPY . .

# Copy in cron setup script
COPY docker-entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set ENV for documentation (actual values come from .env)
ENV CRON_SCHEDULE="0 * * * *"
ENV USERNAMES=""
ENV DISCORD_ENABLED="false"
ENV DISCORD_WEBHOOK=""
ENV CALLMEBOT_ENABLED="false"
ENV CALLMEBOT_PHONE=""
ENV CALLMEBOT_APIKEY=""

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
