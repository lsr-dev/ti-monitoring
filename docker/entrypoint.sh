#!/bin/bash

set -euxo pipefail

if [ "$1" = "app" ]; then
	# Start the web application
	shift
	exec gunicorn -b :8080 app:app
elif [ "$1" = "cron" ]; then
    # Start the cron job
	shift
	exec python /app/cron.py "$@"
else
	# Start what the user passes
	exec "$@"
fi
