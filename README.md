# Game Analytics Dashboard

A real-time game data analytics platform built with Flask, ClickHouse, and ECharts.

## Features

- **Real-time Overview**: Monitor DAU (Daily Active Users), match counts, skin sales, and total revenue.
- **Player Distribution**: Visualize player level distribution with interactive charts.
- **Unified API**: Standardized API response format for better frontend-backend integration.
- **Data Visualization**: Beautiful dashboard powered by ECharts for clear data insights.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: ClickHouse
- **Frontend**: HTML5, CSS3, JavaScript, ECharts
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.x

### Installation & Running

1. **Start ClickHouse**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Data Simulation (Optional)**:
   ```bash
   python3 simulate.py
   ```

4. **Start the Flask Application**:
   ```bash
   python3 app.py
   ```

5. **Access the Dashboard**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## API Endpoints

- `GET /`: The analytics dashboard.
- `GET /api/overview`: Returns daily statistics (DAU, matches, revenue).
- `GET /api/level-distribution`: Returns player level distribution data.
