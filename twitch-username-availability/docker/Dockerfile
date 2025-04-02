FROM python:3.12-slim

WORKDIR /app

# Install curl + cron
RUN apt-get update && apt-get install -y curl cron && apt-get clean

# Copy requirements and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install-deps && \
    playwright install

# Copy app code
COPY . .

# Make entrypoint script executable
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Declare env vars (documented defaults)
ENV USERNAMES=""
ENV DISCORD_ENABLED=false
ENV DISCORD_WEBHOOK=""
ENV CALLMEBOT_ENABLED=false
ENV CALLMEBOT_PHONE=""
ENV CALLMEBOT_APIKEY=""
ENV CRON_SCHEDULE="0 * * * *"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
