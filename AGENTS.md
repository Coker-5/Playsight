# AGENTS.md - Game Analytics Dashboard

Guidelines for AI coding agents working in this repository.

## Project Overview

A real-time game data analytics platform with:
- **Python (Flask)**: Web API and dashboard backend
- **Database**: ClickHouse for analytics storage
- **Message Queue**: Kafka for event streaming
- **Frontend**: HTML/CSS/JS with ECharts visualization

## Developer Commands

### Setup & Run

```bash
# Install dependencies
uv sync

# Start infrastructure (ClickHouse + Kafka)
docker-compose up -d

# Run Flask application
uv run main.py

# Run Kafka consumer (writes events to ClickHouse)
uv run scripts/consume.py

# Run data simulator (generates events to Kafka continuously, ~500 events/hour)
uv run scripts/simulate.py
```

### Production (gunicorn)

```bash
# Serve with gunicorn (installed in pyproject.toml)
uv run gunicorn -w 4 -b 0.0.0.0:5000 "game_analytics:create_app()"
```

### Infrastructure

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Access ClickHouse CLI
docker exec -it clickhouse clickhouse-client
```

### Manual Testing

No test suite is configured. Verify via:

```bash
curl http://127.0.0.1:5000/api/overview
curl http://127.0.0.1:5000/api/level-distribution
curl http://127.0.0.1:5000/api/funnel/default
curl http://127.0.0.1:5000/api/retention/2026-03-30
curl "http://127.0.0.1:5000/api/retention/trend?days=7"
curl -X POST http://127.0.0.1:5000/api/query-sql -H "Content-Type: application/json" -d '{"sql": "SELECT * FROM game_events LIMIT 10"}'
```

## Architecture

### Data Flow

```
Simulator (continuous) → Kafka (tp_game_events) → Consumer → ClickHouse
                                                              ↓
                                              Flask Backend ← Dashboard UI
```

### ClickHouse Tables

- `game_events` - Main event table (MergeTree, partitioned by day)
- `users` - User tracking table
- `users_auto_mv` - Materialized view for auto user creation
- `daily_metrics` - Pre-aggregated daily counts/revenue by event_name (SummingMergeTree)
- `daily_metrics_mv` - Auto-populated from game_events INSERTs
- `daily_active_users` - Deduplicated daily active users (ReplacingMergeTree)
- `daily_active_users_mv` - Auto-populated from game_events INSERTs

**Note:** Repository layer auto-detects if materialized views exist. If not, it falls back to scanning `game_events` directly.

### Package Structure

```
game_analytics/          # Flask package
├── __init__.py         # Exports create_app, Config
├── app.py              # App factory, make_response helper, registers blueprints
├── config.py           # Config class (reads env vars)
├── models/             # Data models (Event dataclass)
├── repositories/       # ClickHouse data access (singleton pattern)
├── services/           # Business logic (AnalyticsService, EventSimulator)
└── routes/             # Blueprint-based API routes
    ├── overview.py     # GET /api/overview
    ├── distribution.py # GET /api/level-distribution
    ├── retention.py    # GET /api/retention/<date>, GET /api/retention/trend
    ├── funnel.py       # GET /api/funnel/default (windowFunnel conversion)
    └── query.py        # POST /api/query-sql

scripts/                # Executable scripts
├── simulate.py                     # Event simulator (main)
├── consume.py                      # Kafka consumer
├── simulate_patch.py               # Simulator patch/utility
├── insert_specific_date.py         # Backfill data for specific dates
└── create_daily_metrics_mv.sql     # DDL for materialized views (run once)

main.py                 # Entry point (creates app, runs dev server on 0.0.0.0:5000)
templates/index.html    # Dashboard UI
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard UI |
| GET | `/api/overview` | Daily stats (DAU, matches, revenue) |
| GET | `/api/level-distribution` | Player level distribution |
| GET | `/api/funnel/default` | Today's conversion funnel: `match_start → match_end → skin_buy` (windowFunnel 7200s) |
| GET | `/api/retention/<date>` | Retention for specific date (day-1, day-3, day-7) |
| GET | `/api/retention/trend?days=N` | Retention trend for last N days |
| POST | `/api/query-sql` | Execute custom ClickHouse SQL |

## Code Conventions

- **Python**: 3.14, managed by `uv` (not pip)
- **Package manager**: Always use `uv sync` and `uv run`
- **Quotes**: Double quotes for strings
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Comments**: Chinese for business logic, English for technical notes
- **Error handling**: Catch specific exceptions, never bare `except:`
- **API responses**: Use `make_response()` from `app.py` returning `{code, data, msg}`
- **Repositories**: Singleton pattern
- **Models**: Use `@dataclass` with type annotations

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_HOST` | `localhost` | ClickHouse host |
| `CLICKHOUSE_PORT` | `8123` | ClickHouse HTTP port |
| `CLICKHOUSE_DATABASE` | `game` | Database name |
| `KAFKA_BOOTSTRAP_SERVERS` | `localhost:9092` | Kafka brokers |
| `KAFKA_TOPIC_EVENTS` | `tp_game_events` | Kafka topic |
| `FLASK_PORT` | `5000` | Flask port |
| `FLASK_DEBUG` | `true` | Debug mode |
| `SIMULATE_SPEED_UP` | `60` | Simulator speed multiplier |

## Gotchas

- **Kafka advertised listeners**: `docker-compose.yml` uses `localhost:9092`. For remote deployment, change `KAFKA_ADVERTISED_LISTENERS` to the server's internal IP (see DEPLOY.md)
- **main.py disables SERVER_NAME**: `app.config["SERVER_NAME"] = None` is set after create_app() - do not remove
- **main.py runs with debug=False**: Despite `FLASK_DEBUG` defaulting to `true`, main.py explicitly sets `debug=False`
- **ClickHouse schema not auto-created**: Tables must be created manually (see DEPLOY.md for DDL)
- **Materialized views are optional**: Repository auto-detects and falls back to `game_events` scan if MVs don't exist
- **Simulator runs continuously**: It does not stop on its own; use Ctrl+C to terminate
- **Topic auto-creation**: Kafka is configured with `KAFKA_AUTO_CREATE_TOPICS_ENABLE=true`

## Git

- No pre-commit hooks
- Commit messages: English, describe the "why"
