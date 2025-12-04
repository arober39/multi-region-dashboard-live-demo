#!/bin/bash

# Load environment variables
set -a
source .env
set +a

echo "Running migrations for all regions..."
echo ""

# US East
if [ -n "$AIVEN_PG_US_EAST" ]; then
    echo "=== Migrating US East ==="
    psql "$AIVEN_PG_US_EAST" < migrations/001_create_health_check_tables.sql
    echo ""
else
    echo "Skipping US East (no connection string)"
    echo ""
fi

# EU West
if [ -n "$AIVEN_PG_EU_WEST" ]; then
    echo "=== Migrating EU West ==="
    psql "$AIVEN_PG_EU_WEST" < migrations/001_create_health_check_tables.sql
    echo ""
else
    echo "Skipping EU West (no connection string)"
    echo ""
fi

# Asia Pacific
if [ -n "$AIVEN_PG_ASIA_PACIFIC" ]; then
    echo "=== Migrating Asia Pacific ==="
    psql "$AIVEN_PG_ASIA_PACIFIC" < migrations/001_create_health_check_tables.sql
    echo ""
else
    echo "Skipping Asia Pacific (no connection string)"
    echo ""
fi

echo "Migration complete!"
