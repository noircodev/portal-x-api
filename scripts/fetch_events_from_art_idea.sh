#!/bin/bash

mkdir -p /home/web/app/logs

touch /home/web/app/logs/cron.log
chmod 664 /home/web/app/logs/cron.log

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Output:"
    /home/web/app/.venv/bin/python /home/web/app/manage.py fetch_events -e artidea
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished fetching events from Art Idea."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Completed."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ----------------------------------------"
} >>/home/web/app/logs/cron.log 2>&1
