#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running DB Upgrade..."
flask db upgrade

# Exec the container's main process (CMD in Dockerfile)
echo "Starting Gunicorn..."
exec "$@"
