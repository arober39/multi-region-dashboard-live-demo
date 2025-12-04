# Database Migrations

This directory contains SQL migration files for the Multi-Region Dashboard.

## Running Migrations

To create the health check tables, run the migration SQL file against each of your regional databases:

```bash
# For each region, run:
psql "your-database-connection-string" < migrations/001_create_health_check_tables.sql
```

Or using the environment variables from your `.env` file:

```bash
# US East
psql "$AIVEN_PG_US_EAST" < migrations/001_create_health_check_tables.sql

# EU West
psql "$AIVEN_PG_EU_WEST" < migrations/001_create_health_check_tables.sql

# Asia Pacific
psql "$AIVEN_PG_ASIA_PACIFIC" < migrations/001_create_health_check_tables.sql
```

## Tables Created

### connection_checks
Stores results from connection tests including latency, server info, and errors.

### latency_checks
Stores results from latency measurements with multiple iterations.

### load_test_checks
Stores results from load testing with concurrent connections.

### health_metrics_checks
Stores database health metrics including cache hit ratio, connections, and database size.

## Views

### recent_connection_checks
Summary view of connection checks from the last 24 hours per region.

### recent_health_metrics
Summary view of health metrics from the last 24 hours per region.

## Maintenance

The migration includes a `cleanup_old_checks()` function that removes data older than 7 days. You can set up a cron job or scheduled task to run this periodically:

```sql
SELECT cleanup_old_checks();
```

## Querying Check History

Example queries:

```sql
-- Get last 10 connection checks for a region
SELECT * FROM connection_checks
WHERE region_id = 'us-east'
ORDER BY checked_at DESC
LIMIT 10;

-- Get 24-hour summary for all regions
SELECT * FROM recent_connection_checks;

-- Get average latency by region over last hour
SELECT
    region_id,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as check_count
FROM connection_checks
WHERE checked_at > NOW() - INTERVAL '1 hour'
  AND success = true
GROUP BY region_id;

-- Get health metrics trend
SELECT
    region_id,
    date_trunc('hour', checked_at) as hour,
    AVG(cache_hit_ratio) as avg_cache_hit,
    AVG(active_connections) as avg_active_conn
FROM health_metrics_checks
WHERE checked_at > NOW() - INTERVAL '24 hours'
  AND success = true
GROUP BY region_id, hour
ORDER BY hour DESC;
```

## API Integration

The application automatically saves check results to these tables when you run tests through the web interface. The following functions are called:

- `save_connection_check()` - Called after each connection test
- `save_latency_check()` - Called after each latency measurement
- `save_load_test_check()` - Called after each load test
- `save_health_metrics_check()` - Called after each health check

You can also retrieve historical data using:

- `get_recent_connection_checks(region_id, limit=10)` - Get recent checks
- `get_connection_check_summary(region_id)` - Get 24-hour summary
