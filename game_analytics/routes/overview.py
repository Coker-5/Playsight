"""概览相关路由"""

from flask import Blueprint, render_template

from game_analytics.app import make_response
from game_analytics.services import AnalyticsService

bp = Blueprint("overview", __name__)


@bp.route("/")
def index():
    """首页"""
    return render_template("index.html")


@bp.route("/api/overview")
def overview():
    """概览数据 API"""
    data = AnalyticsService.get_overview_data()
    return make_response(data=data)
