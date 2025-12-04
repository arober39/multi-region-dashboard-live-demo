# Multi-Region PostgreSQL Testing Dashboard

An interactive web dashboard for testing PostgreSQL connectivity and performance across multiple Aiven database regions. Built with FastAPI, HTMX, and LaunchDarkly for feature flag management.

## Features

- **Multi-Region Connectivity Testing**: Test connections to PostgreSQL databases across different geographic regions (US East, EU West, Asia Pacific)
- **Performance Metrics**: Measure latency, connection times, and database health metrics
- **Health Checks**: Monitor database health including cache hit ratios, connection counts, and query statistics
- **Load Testing**: Run concurrent connection tests to evaluate database performance
- **Real-Time Updates**: Auto-refreshing dashboard with configurable refresh intervals
- **Feature Flag Integration**: LaunchDarkly integration for controlling features and regions dynamically
- **Query Statistics**: View pg_stat_statements data for top queries and performance insights
- **Privilege-Aware**: Gracefully handles insufficient database privileges without breaking the UI

## Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL via Aiven
- **Frontend**: HTMX, Bootstrap 5, Jinja2 templates
- **Feature Flags**: LaunchDarkly Server SDK
- **Database Driver**: asyncpg

## Prerequisites

- Python 3.8 or higher
- PostgreSQL databases in Aiven (or compatible PostgreSQL instances)
- LaunchDarkly account and SDK key (optional, but recommended)
- Environment variables configured (see Configuration section)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multi-region-dashboard-live-demo
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the root directory (see Configuration section)

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

   The dashboard will be available at `http://localhost:8000`

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Aiven PostgreSQL Connection Strings
AIVEN_PG_US_EAST=postgresql://user:password@host:port/database?sslmode=require
AIVEN_PG_EU_WEST=postgresql://user:password@host:port/database?sslmode=require
AIVEN_PG_ASIA_PACIFIC=postgresql://user:password@host:port/database?sslmode=require

# LaunchDarkly SDK Key (optional)
LAUNCHDARKLY_SDK_KEY=your-sdk-key-here
```

### Connection String Format

Aiven PostgreSQL connection strings should follow this format:
```
postgresql://[user]:[password]@[host]:[port]/[database]?sslmode=require
```

You can find your connection strings in the Aiven console under your service's "Overview" tab.

## LaunchDarkly Feature Flags

The dashboard uses LaunchDarkly to control features and region availability. The following feature flags are configured in the `multi-regions-live-demo-dashboard` project:

### Region Flags
- `region-us-east-enabled` - Controls US East (Virginia) region availability
- `region-eu-west-enabled` - Controls EU West (Ireland) region availability
- `region-asia-pacific-enabled` - Controls Asia Pacific (Singapore) region availability

### Feature Flags
- `enable-test-all-regions` - Enables/disables the "Test All Regions" functionality
- `enable-health-checks` - Enables/disables health check features
- `enable-load-testing` - Enables/disables load testing features
- `dashboard-refresh-seconds` - Controls auto-refresh interval (numeric: 15, 30, or 60 seconds)

### Setting Up Feature Flags

1. Log in to your LaunchDarkly account
2. Navigate to the `multi-regions-live-demo-dashboard` project
3. Ensure all feature flags are created and configured
4. Set the flags to ON in your desired environments (Test/Production)
5. Configure targeting rules as needed

## Usage

### Dashboard Overview

The main dashboard provides:

1. **Quick Actions**: Test all regions simultaneously
2. **Live Status**: Real-time latency for all enabled regions
3. **Individual Region Testing**: Per-region testing controls

### Available Actions

- **Test Connection**: Verify connectivity to a specific region
- **Measure Latency**: Run multiple iterations to measure average latency
- **Health Check**: View database health metrics including:
  - Cache hit ratio
  - Active/idle/total connections
  - Database size
  - Query statistics (pg_stat_statements) if available
- **Load Test**: Run concurrent connection tests (requires `enable-load-testing` flag)

### API Endpoints

#### Page Routes
- `GET /` - Main dashboard page

#### API Routes
- `POST /api/regions/{region_id}/test` - Test connection to a region
- `POST /api/regions/{region_id}/latency?iterations=5` - Measure latency
- `POST /api/regions/{region_id}/health` - Get health metrics
- `POST /api/regions/{region_id}/load-test?concurrent=10` - Run load test
- `POST /api/regions/test-all` - Test all enabled regions
- `GET /api/regions/summary` - Get summary for auto-refresh

All API endpoints respect LaunchDarkly feature flags and region availability.

## Project Structure

```
multi-region-dashboard-live-demo/
├── app/
│   ├── __init__.py
│   ├── config.py              # Region configurations
│   ├── database.py             # Database connection & queries
│   ├── feature_flags.py        # LaunchDarkly integration
│   ├── main.py                 # FastAPI application
│   ├── queries.py              # SQL query definitions
│   ├── routers/
│   │   ├── api.py             # HTMX API endpoints
│   │   └── pages.py           # Page routes
│   ├── static/                 # Static assets (CSS, JS)
│   └── templates/              # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       └── partials/           # HTMX partials
├── requirements.txt
└── README.md
```

## Health Checks

Health checks provide comprehensive database metrics:

- **Cache Hit Ratio**: Percentage of database blocks served from cache
- **Connection Statistics**: Active, idle, and total connections
- **Database Size**: Formatted database size
- **Query Statistics**: Top queries from pg_stat_statements (if extension enabled)

Health checks gracefully handle insufficient privileges by:
- Filtering out data that requires elevated permissions
- Displaying warnings for unavailable metrics
- Continuing to show available data

## Troubleshooting

### Connection Issues

- **SSL Required**: Ensure connection strings include `?sslmode=require`
- **Network Access**: Verify Aiven firewall rules allow your IP address
- **Credentials**: Double-check username and password in connection strings

### Feature Flags Not Working

- **SDK Key**: Verify `LAUNCHDARKLY_SDK_KEY` is set correctly
- **Flag Status**: Check that flags are enabled in LaunchDarkly dashboard
- **Environment**: Ensure you're using the correct environment (Test/Production)

### Health Check Errors

- **Privileges**: Some metrics require superuser privileges. The dashboard will show warnings for unavailable data.
- **pg_stat_statements**: The extension must be enabled on your PostgreSQL instance to view query statistics.

### Database Privileges

The dashboard handles insufficient privileges gracefully:
- Metrics requiring privileges show as "N/A"
- Warnings are displayed for unavailable data
- The dashboard continues to function with available metrics

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Adding New Regions

Edit `app/config.py` to add new regions:

```python
REGIONS: dict[str, RegionConfig] = {
    "new-region": RegionConfig(
        id="new-region",
        name="New Region Name",
        env_key="AIVEN_PG_NEW_REGION",
        latitude=0.0,
        longitude=0.0,
    ),
    # ... existing regions
}
```

Then create the corresponding feature flag: `region-new-region-enabled`

## Dependencies

- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `jinja2>=3.1.2` - Template engine
- `python-dotenv>=1.0.0` - Environment variable management
- `launchdarkly-server-sdk>=9.0.0` - Feature flag SDK

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions:
- Check the troubleshooting section above
- Review LaunchDarkly documentation for feature flag setup
- Consult Aiven documentation for database configuration

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [Aiven](https://aiven.io/) for PostgreSQL hosting
- Feature flags managed by [LaunchDarkly](https://launchdarkly.com/)

