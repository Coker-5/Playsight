# Game Analytics Dashboard

A real-time game data analytics platform built with Flask, ClickHouse, and ECharts.

## Features

- **Real-time Overview**: Monitor DAU (Daily Active Users), match counts, skin sales, and total revenue.
- **Player Distribution**: Visualize player level distribution with interactive charts.
- **Retention Analytics**: Track day-1, day-3, and day-7 retention rates with trend visualization.
- **SQL Console**: Execute custom ClickHouse SQL queries directly from the dashboard.
- **Continuous Data Generation**: Automated event simulator running 24/7 with realistic intervals.
- **Data Visualization**: Beautiful dashboard powered by ECharts for clear data insights.

<img width="2166" height="1217" alt="image" src="https://github.com/user-attachments/assets/55500df1-d7e4-48dd-a092-23b49b985acd" />

## Project Structure

```
game-analytics/
├── main.py                   # Flask application entry
├── game_analytics/           # Main package
│   ├── app.py               # Flask app factory
│   ├── config.py            # Configuration
│   ├── models/              # Data models (Event)
│   ├── repositories/        # Data access layer (ClickHouse)
│   ├── services/            # Business logic
│   └── routes/              # API routes
├── scripts/                  # Executable scripts
│   ├── simulate.py          # Event simulator
│   └── consume.py           # Kafka consumer
├── templates/               # HTML templates
├── docker-compose.yml       # Docker services
└── pyproject.toml           # Python dependencies
```
>>>>>>> 92380cf (Add retention analytics dashboard and continuous data simulator)

## Tech Stack

- **Backend**: Flask (Python 3.14+)
- **Database**: ClickHouse
- **Message Queue**: Kafka
- **Frontend**: HTML5, CSS3, JavaScript, ECharts
- **Containerization**: Docker & Docker Compose
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) installed

### Installation & Running

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Run Data Simulator** (generate events to Kafka):
   ```bash
   uv run scripts/simulate.py
   ```

4. **Run Kafka Consumer** (write to ClickHouse):
   ```bash
   uv run scripts/consume.py
   ```

5. **Start Flask Application**:
   ```bash
   uv run main.py
   ```

6. **Access the Dashboard**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## API Endpoints

- `GET /`: The analytics dashboard
- `GET /api/overview`: Returns daily statistics (DAU, matches, revenue)
- `GET /api/level-distribution`: Returns player level distribution data
- `POST /api/query-sql`: Execute custom SQL queries

## Environment Variables

- `CLICKHOUSE_HOST` - ClickHouse host (default: localhost)
- `CLICKHOUSE_PORT` - ClickHouse port (default: 8123)
- `CLICKHOUSE_DATABASE` - Database name (default: game)
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka brokers (default: localhost:9092)
- `FLASK_PORT` - Flask server port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: true)

## Architecture

- **Models**: Data model definitions (Event dataclass)
- **Repositories**: ClickHouse data access with singleton pattern
- **Services**: Business logic layer
- **Routes**: Flask blueprint-based API routes
