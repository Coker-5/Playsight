"""留存分析相关路由"""

from flask import Blueprint, request

from game_analytics.app import make_response
from game_analytics.repositories import repo

bp = Blueprint("retention", __name__)


@bp.route("/api/retention/<date>")
def get_retention(date):
    """获取指定日期的留存数据"""
    data = repo.get_retention_data(date)
    return make_response(data=data)


@bp.route("/api/retention/trend")
def get_retention_trend():
    """获取留存趋势数据"""
    days = request.args.get("days", 7, type=int)
    data = repo.get_daily_retention_trend(days)
    return make_response(data={"trend": data})
