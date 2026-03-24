"""SQL 查询路由"""

from flask import Blueprint, request

from game_analytics.app import make_response
from game_analytics.services import AnalyticsService

bp = Blueprint("query", __name__)


@bp.route("/api/query-sql", methods=["POST"])
def query_sql():
    """自定义 SQL 查询 API"""
    sql = request.json.get("sql")
    if not sql:
        return make_response(code=400, msg="SQL is required")

    try:
        result = AnalyticsService.execute_custom_query(sql)
        return make_response(data=result)
    except Exception as e:
        return make_response(code=500, msg=str(e))
