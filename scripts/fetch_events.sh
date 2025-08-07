#!/bin/bash

mkdir -p /home/web/app/logs

touch /home/web/app/logs/cron.log
chmod 664 /home/web/app/logs/cron.log

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Output:"
    /home/web/app/.venv/bin/python /home/web/app/manage.py fetch_events -e serp_api_google_event
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished fetching events from Google Events via SerpAPI."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Completed."
} >>/home/web/app/logs/cron.log 2>&1
