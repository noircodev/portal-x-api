#!/bin/bash

mkdir -p /home/web/app/logs

touch /home/web/app/logs/cron.log
chmod 664 /home/web/app/logs/cron.log

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Output:"
    /home/web/app/.venv/bin/python /home/web/app/manage.py fetch_events -e all_events
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished fetching events from allevents.in."
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Completed."
} >>/home/web/app/logs/cron.log 2>&1
