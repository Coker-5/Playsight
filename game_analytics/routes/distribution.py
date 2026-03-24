"""分布查询路由"""

from flask import Blueprint

from game_analytics.app import make_response
from game_analytics.services import AnalyticsService

bp = Blueprint("distribution", __name__)


@bp.route("/api/level-distribution")
def level_distribution():
    """段位分布 API"""
    data = AnalyticsService.get_level_distribution()
    return make_response(data=data)
