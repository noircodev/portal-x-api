#!/bin/bash

mkdir -p /home/web/app/logs

touch /home/web/app/logs/meili.log
chmod 664 /home/web/app/logs/meili.log

{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cron Job Output:"
    /home/web/app/.venv/bin/python /home/web/app/manage.py sync_search_index
} >>/home/web/app/logs/meili.log 2>&1
