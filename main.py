"""
应用入口
"""

from game_analytics import create_app
from game_analytics.config import Config

app = create_app()

if __name__ == "__main__":
    # 生产环境建议设置 host='0.0.0.0' 以允许外部访问
    # 或通过 nginx 反向代理
    host = "0.0.0.0" if not Config.FLASK_DEBUG else "127.0.0.1"
    app.run(host=host, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
