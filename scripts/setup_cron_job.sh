#!/bin/bash

# Path to the scripts
SCRIPTS_DIR="/home/web/app/scripts"

# Define the cron jobs
CRON_JOBS=(
    "0 12 */14 * * $SCRIPTS_DIR/fetch_events.sh"
    "0 8 * * 1,3,5,7 $SCRIPTS_DIR/fetch_events_from_eventbrite.sh"
    "0 8 * * 2,4,6 $SCRIPTS_DIR/fetch_events_from_all_events.sh"
    "0 9 */7 * * $SCRIPTS_DIR/fetch_events_from_art_idea.sh"
    "0 0 * * * $SCRIPTS_DIR/sync_meili.sh"
)

# Get the current user's crontab
CRONTAB_TMP=$(mktemp)
crontab -l >"$CRONTAB_TMP" 2>/dev/null || true

# Add missing cron jobs
for job in "${CRON_JOBS[@]}"; do
    if ! grep -Fq "$job" "$CRONTAB_TMP"; then
        echo "Adding job: $job"
        echo "$job" >>"$CRONTAB_TMP"
    else
        echo "Job already exists: $job"
    fi
done

# Install the updated crontab
crontab "$CRONTAB_TMP"
rm "$CRONTAB_TMP"

echo "Crontab setup completed."
