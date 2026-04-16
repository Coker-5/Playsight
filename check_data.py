#!/usr/bin/env uv run python
import sys

sys.path.append(".")

from game_analytics.repositories import repo

print("=== 游戏事件统计 ===")
result = repo.query(
    "SELECT event_name, count(*) as cnt FROM game_events GROUP BY event_name ORDER BY cnt DESC"
)
for row in result.result_rows:
    print(f"  {row[0]}: {row[1]}")

print("\n=== 2026-04-15 用户统计 ===")
result = repo.query("""
    SELECT event_name, count(DISTINCT user_id) as unique_users
    FROM game_events
    WHERE toDate(event_time) = '2026-04-15'
    GROUP BY event_name
    ORDER BY unique_users DESC
""")
for row in result.result_rows:
    print(f"  {row[0]}: {row[1]} unique users")

print("\n=== match_start 事件示例 ===")
result = repo.query("""
    SELECT user_id, event_time, properties
    FROM game_events
    WHERE event_name = 'match_start'
    LIMIT 5
""")
for row in result.result_rows:
    print(f"  User: {row[0]}, Time: {row[1]}, Props: {row[2]}")

print("\n=== 漏斗路径分析 ===")
# 检查用户是否完成了完整的漏斗路径
result = repo.query("""
    SELECT
        u.user_id,
        any(u.first_login_date) as login_date,
        countIf(e.event_name = 'match_start') as match_start_count,
        countIf(e.event_name = 'match_end') as match_end_count,
        countIf(e.event_name = 'skin_buy') as skin_buy_count
    FROM users u
    LEFT JOIN game_events e ON u.user_id = e.user_id
    WHERE u.first_login_date = '2026-04-15'
    GROUP BY u.user_id
    HAVING match_start_count > 0
    ORDER BY u.user_id
    LIMIT 10
""")

print("用户漏斗路径 (前10个):")
for row in result.result_rows:
    print(
        f"  User: {row[0]}, Login: {row[1]}, MatchStart: {row[2]}, MatchEnd: {row[3]}, SkinBuy: {row[4]}"
    )
