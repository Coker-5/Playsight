"""
事件模拟器 - 持续生成游戏事件数据并发送到 Kafka
每小时生成 500 条数据
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import random
import json
import time
import signal
from datetime import datetime, timedelta
from kafka import KafkaProducer

from game_analytics.models import Event
from game_analytics.services import EventSimulator
from game_analytics.config import Config


# ========== 模拟时间设置 ==========
SIMULATE_SPEED_UP = Config.SIMULATE_SPEED_UP
START_TIME = datetime.now()
current_sim_time = START_TIME

# 运行控制
running = True


def signal_handler(signum, frame):
    """处理退出信号"""
    global running
    print("\n接收到退出信号，正在停止...")
    running = False


# 注册信号处理
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_sim_time():
    """获取模拟时间"""
    global current_sim_time
    current_sim_time += timedelta(seconds=random.randint(10, 30))
    return current_sim_time.strftime("%Y-%m-%d %H:%M:%S")


def make_properties(event_name, **kwargs):
    """生成事件属性"""
    if event_name == "match_end":
        return {
            "hero": random.choice(EventSimulator.HEROES),
            "win": random.choice([True, False]),
            "kills": random.randint(0, 15),
            "deaths": random.randint(0, 10),
            "assists": random.randint(0, 20),
            "mvp": random.choice([True, False]),
        }
    elif event_name == "match_start":
        return {
            "hero": random.choice(EventSimulator.HEROES),
            "summoner_skill": random.choice(EventSimulator.DEFAULT_SKILL),
            "rune_level": random.randint(0, 150),
        }
    elif event_name == "skin_buy":
        return {
            "skin_name": random.choice(EventSimulator.SKINS),
            "price": random.choice(EventSimulator.SKIN_PRICES),
        }
    elif event_name == "battle_pass_buy":
        return {"season": random.choice(EventSimulator.SEASONS)}
    else:
        return {}


def make_event(player, event_name, **kwargs):
    """创建事件"""
    event_time_str = get_sim_time()
    return Event(
        event_time=event_time_str,
        event_name=event_name,
        user_id=player["user_id"],
        server=player["server"],
        device=player["device"],
        level=player["level"],
        pay_amount=kwargs.get("pay_amount", 0),
        duration=random.randint(0, 30),
        properties=make_properties(event_name, **kwargs),
    )


# ========== 状态机定义 ==========
VALID_TRANSITIONS = {
    "offline": ["login"],
    "online": ["match_start", "skin_buy", "battle_pass_buy", "logout"],
    "in_match": ["match_end"],
}


def get_next_event(current_status):
    """根据当前状态获取下一个事件"""
    possible_events = VALID_TRANSITIONS.get(current_status, ["login"])
    event_name = random.choice(possible_events)

    next_status = current_status
    if event_name == "login":
        next_status = "online"
    elif event_name == "logout":
        next_status = "offline"
    elif event_name == "match_start":
        next_status = "in_match"
    elif event_name == "match_end":
        next_status = "online"

    return event_name, next_status


def init_players(count=500):
    """初始化玩家列表"""
    return [
        {
            "user_id": f"u_{i:03d}",
            "server": random.choice(EventSimulator.SERVERS),
            "device": random.choice(EventSimulator.DEVICES),
            "level": random.choice(EventSimulator.RANKS),
            "status": "offline",
        }
        for i in range(count)
    ]


def generate_hourly_events(producer, players, events_per_hour=500):
    """生成一小时的事件数据"""
    global current_sim_time

    # 将 500 条数据均匀分布在一小时内
    events = []
    hour_start = current_sim_time
    hour_end = hour_start + timedelta(hours=1)

    for i in range(events_per_hour):
        # 计算这条事件的时间戳（均匀分布）
        progress = i / events_per_hour
        event_time = hour_start + timedelta(seconds=progress * 3600)
        current_sim_time = event_time

        player = random.choice(players)
        event_name, next_status = get_next_event(player["status"])
        event = make_event(player, event_name)

        # 发送事件
        future = producer.send(Config.KAFKA_TOPIC_EVENTS, value=event.to_json())
        future.get(timeout=10)

        print(
            f"[{event_time.strftime('%H:%M:%S')}] "
            f"用户 {player['user_id']} 事件 {event_name}: "
            f"{player['status']} -> {next_status}"
        )

        player["status"] = next_status

    return events_per_hour


def main():
    """主函数 - 持续运行"""
    global current_sim_time

    print("=== 游戏事件模拟器启动 ===")
    print(f"目标: 每小时生成 500 条事件")
    print("按 Ctrl+C 停止运行\n")

    # 初始化 Kafka 生产者
    producer = KafkaProducer(
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: v.encode("utf-8"),
    )

    # 初始化玩家列表
    players = init_players(500)

    total_events = 0
    current_sim_time = datetime.now()

    while running:
        hour_start = datetime.now()
        hour_events = 0

        print(f"\n{'=' * 50}")
        print(f"开始生成 {current_sim_time.strftime('%Y-%m-%d %H:%M')} 的事件数据")
        print(f"{'=' * 50}\n")

        try:
            # 生成 500 条事件
            hour_events = generate_hourly_events(producer, players, 500)
            total_events += hour_events

            print(f"\n本小时生成完成: {hour_events} 条事件")
            print(f"累计生成: {total_events} 条事件")

        except Exception as e:
            print(f"生成事件时出错: {e}")
            time.sleep(5)
            continue

        # 计算还需等待的时间
        elapsed = (datetime.now() - hour_start).total_seconds()
        sleep_time = 3600 - elapsed

        if sleep_time > 0 and running:
            print(f"等待 {sleep_time:.1f} 秒进入下一小时...\n")
            time.sleep(sleep_time)

        # 时间前进一小时
        current_sim_time += timedelta(hours=1)

    print(f"\n模拟器已停止。累计生成 {total_events} 条事件")


if __name__ == "__main__":
    main()
