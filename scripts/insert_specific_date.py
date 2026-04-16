"""
手动插入指定日期的事件数据到Kafka
可以指定日期和事件数量
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import random
import argparse
from datetime import datetime, timedelta
from kafka import KafkaProducer

from game_analytics.models import Event
from game_analytics.services import EventSimulator
from game_analytics.config import Config


def parse_date(date_str):
    """解析日期字符串"""
    return datetime.strptime(date_str, "%Y-%m-%d")


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


def make_event(player, event_name, event_time, **kwargs):
    """创建事件"""
    return Event(
        event_time=event_time,
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
            "user_id": f"user_{args.date}_{i:03d}",
            "server": random.choice(EventSimulator.SERVERS),
            "device": random.choice(EventSimulator.DEVICES),
            "level": random.choice(EventSimulator.RANKS),
            "status": "offline",
        }
        for i in range(count)
    ]


def generate_events_for_date(target_date, event_count, events_per_user=10):
    """为指定日期生成事件"""
    print(f"为日期 {target_date.strftime('%Y-%m-%d')} 生成 {event_count} 条事件")

    # 计算需要的用户数量
    user_count = max(1, event_count // events_per_user)
    players = init_players(user_count)

    # 初始化 Kafka 生产者
    producer = KafkaProducer(
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: v.encode("utf-8"),
    )

    events_generated = 0
    target_datetime = datetime.combine(target_date, datetime.min.time())

    print(f"目标用户数: {len(players)}")
    print(f"预计每个用户事件数: {events_per_user}")
    print("生成中...")

    while events_generated < event_count:
        # 随机选择一个玩家
        player = random.choice(players)

        # 生成事件时间（在目标日期内随机分布）
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        event_time = target_datetime + timedelta(
            hours=hours, minutes=minutes, seconds=seconds
        )
        event_time_str = event_time.strftime("%Y-%m-%d %H:%M:%S")

        # 生成事件
        event_name, next_status = get_next_event(player["status"])
        event = make_event(player, event_name, event_time_str)

        # 发送事件到Kafka
        producer.send(Config.KAFKA_TOPIC_EVENTS, value=event.to_json())

        events_generated += 1
        player["status"] = next_status

        # 每100条打印一次进度
        if events_generated % 100 == 0:
            print(f"  已生成 {events_generated}/{event_count} 条事件")

    producer.flush()
    producer.close()

    print(f"✓ 完成！已生成 {events_generated} 条事件")
    print(f"事件时间范围: {target_date.strftime('%Y-%m-%d')} 00:00:00 - 23:59:59")
    print(f"涉及用户: {[p['user_id'] for p in players[:5]]}...")  # 只显示前5个用户


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="手动插入指定日期的事件数据")
    parser.add_argument(
        "--date", type=str, required=True, help="目标日期 (格式: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--count", type=int, default=500, help="要生成的事件数量 (默认: 500)"
    )
    parser.add_argument(
        "--events-per-user", type=int, default=10, help="每个用户平均事件数 (默认: 10)"
    )

    args = parser.parse_args()

    try:
        target_date = parse_date(args.date)
        generate_events_for_date(target_date, args.count, args.events_per_user)
    except ValueError as e:
        print(f"日期格式错误: {e}")
        print("请使用 YYYY-MM-DD 格式，例如: 2026-03-30")
    except Exception as e:
        print(f"生成事件时出错: {e}")
