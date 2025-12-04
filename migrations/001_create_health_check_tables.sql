-- Multi-Region Dashboard Health Check Tables
-- Migration: 001_create_health_check_tables.sql

-- Table to store connection test results
CREATE TABLE IF NOT EXISTS connection_checks (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    latency_ms NUMERIC(10, 2),
    server_ip VARCHAR(50),
    backend_pid INTEGER,
    pg_version TEXT,
    error_message TEXT,
    user_key VARCHAR(255)
);

-- Table to store latency measurement results
CREATE TABLE IF NOT EXISTS latency_checks (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    iterations INTEGER NOT NULL,
    min_ms NUMERIC(10, 2),
    max_ms NUMERIC(10, 2),
    avg_ms NUMERIC(10, 2),
    timings JSONB,
    error_message TEXT,
    user_key VARCHAR(255)
);

-- Table to store load test results
CREATE TABLE IF NOT EXISTS load_test_checks (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    concurrent_connections INTEGER NOT NULL,
    min_ms NUMERIC(10, 2),
    max_ms NUMERIC(10, 2),
    avg_ms NUMERIC(10, 2),
    total_time_ms NUMERIC(10, 2),
    queries_per_second NUMERIC(10, 2),
    error_message TEXT,
    user_key VARCHAR(255)
);

-- Table to store health metrics
CREATE TABLE IF NOT EXISTS health_metrics_checks (
    id SERIAL PRIMARY KEY,
    region_id VARCHAR(50) NOT NULL,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    cache_hit_ratio NUMERIC(5, 2),
    active_connections INTEGER,
    idle_connections INTEGER,
    total_connections INTEGER,
    db_size VARCHAR(50),
    pg_stat_statements_available BOOLEAN,
    warnings JSONB,
    error_message TEXT,
    user_key VARCHAR(255)
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_connection_checks_region_time ON connection_checks(region_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_latency_checks_region_time ON latency_checks(region_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_load_test_checks_region_time ON load_test_checks(region_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_health_metrics_checks_region_time ON health_metrics_checks(region_id, checked_at DESC);

-- Indexes for user_key lookups (for analytics)
CREATE INDEX IF NOT EXISTS idx_connection_checks_user_key ON connection_checks(user_key);
CREATE INDEX IF NOT EXISTS idx_latency_checks_user_key ON latency_checks(user_key);
CREATE INDEX IF NOT EXISTS idx_load_test_checks_user_key ON load_test_checks(user_key);
CREATE INDEX IF NOT EXISTS idx_health_metrics_checks_user_key ON health_metrics_checks(user_key);

-- View for recent connection check summary (last 24 hours)
CREATE OR REPLACE VIEW recent_connection_checks AS
SELECT
    region_id,
    COUNT(*) as total_checks,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_checks,
    AVG(CASE WHEN success THEN latency_ms ELSE NULL END) as avg_latency_ms,
    MIN(CASE WHEN success THEN latency_ms ELSE NULL END) as min_latency_ms,
    MAX(CASE WHEN success THEN latency_ms ELSE NULL END) as max_latency_ms,
    MAX(checked_at) as last_check_at
FROM connection_checks
WHERE checked_at > NOW() - INTERVAL '24 hours'
GROUP BY region_id;

-- View for health metrics trends (last 24 hours)
CREATE OR REPLACE VIEW recent_health_metrics AS
SELECT
    region_id,
    COUNT(*) as total_checks,
    AVG(cache_hit_ratio) as avg_cache_hit_ratio,
    AVG(active_connections) as avg_active_connections,
    AVG(total_connections) as avg_total_connections,
    MAX(checked_at) as last_check_at
FROM health_metrics_checks
WHERE checked_at > NOW() - INTERVAL '24 hours'
  AND success = TRUE
GROUP BY region_id;

-- Function to clean up old check data (keep last 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_checks()
RETURNS void AS $$
BEGIN
    DELETE FROM connection_checks WHERE checked_at < NOW() - INTERVAL '7 days';
    DELETE FROM latency_checks WHERE checked_at < NOW() - INTERVAL '7 days';
    DELETE FROM load_test_checks WHERE checked_at < NOW() - INTERVAL '7 days';
    DELETE FROM health_metrics_checks WHERE checked_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
