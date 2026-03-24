"""配置模块"""

import os


class Config:
    """应用配置"""

    # ClickHouse 配置
    CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
    CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "game")

    # Kafka 配置
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_EVENTS = os.getenv("KAFKA_TOPIC_EVENTS", "tp_game_events")

    # Flask 配置
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # 模拟器配置
    SIMULATE_SPEED_UP = int(os.getenv("SIMULATE_SPEED_UP", "60"))
