#!/bin/sh
set -e

# Activation du service de cron si non actif
ps | grep "[c]rond" || crond -b

/docker-entrypoint.sh "$@"
