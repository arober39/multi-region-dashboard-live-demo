#!/bin/bash
set -a
source .env
set +a

echo "Checking tables in US East..."
/opt/homebrew/opt/postgresql@17/bin/psql "$AIVEN_PG_US_EAST" -c "\dt" | grep checks
