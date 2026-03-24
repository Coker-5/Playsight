"""
业务逻辑服务层
"""

from typing import Dict, Any, List, Tuple

from game_analytics.repositories import repo


class AnalyticsService:
    """Analytics 业务服务"""

    @staticmethod
    def get_overview_data() -> Dict[str, Any]:
        """获取概览页面数据"""
        today_sales = repo.get_today_skin_sales()
        total_sales = repo.get_total_skin_sales()

        return {
            "today": {
                "dau": repo.get_today_dau(),
                "match": repo.get_today_match_count(),
                "skin_sell_count": today_sales[0],
                "revenue": today_sales[1],
            },
            "total": {
                "players": repo.get_total_players(),
                "match": repo.get_total_match_count(),
                "skin_sell_count": total_sales[0],
                "revenue": total_sales[1],
            },
        }

    @staticmethod
    def get_level_distribution() -> Dict[str, List[Tuple]]:
        """获取段位分布"""
        return {"level_distribution": repo.get_level_distribution()}

    @staticmethod
    def execute_custom_query(sql: str) -> Dict[str, Any]:
        """执行自定义 SQL 查询"""
        return repo.execute_sql(sql)


class EventSimulator:
    """事件模拟器服务"""

    # 基础数据常量
    SERVERS = [
        "QQ第1区",
        "QQ第2区",
        "QQ第3区",
        "QQ第4区",
        "微信第1区",
        "微信第2区",
        "微信第3区",
        "微信第4区",
    ]
    DEVICES = ["iOS", "Android"]
    SEASONS = ["S33", "S34", "S35", "S36", "S37"]
    RANKS = ["黄金", "铂金", "钻石", "星耀", "王者"]
    HEROES = ["李白", "妲己", "后羿", "貂蝉", "韩信", "孙悟空", "铠", "张飞"]
    DEFAULT_SKILL = [
        "惩击",
        "终结",
        "狂暴",
        "疾跑",
        "治疗术",
        "干扰",
        "眩晕",
        "净化",
        "弱化",
        "闪现",
    ]
    SKINS = [
        "李白·千年之狐",
        "后羿·弈",
        "韩信·绝世天君",
        "孙悟空·地狱火",
        "貂蝉·仲夏夜之梦",
        "铠·青龙志",
        "妲己·热情桑巴",
        "张飞·虎魄",
        "鲁班七号·电玩小子",
        "小乔·天鹅之梦",
        "孙尚香·末日机甲",
        "吕布·天魔缭乱",
        "赵云·引擎之心",
    ]
    SKIN_PRICES = [38, 88, 188, 288, 388]
