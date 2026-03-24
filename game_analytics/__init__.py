"""
Game Analytics Package
实时游戏数据 analytics 平台
"""

from .config import Config
from .app import create_app

__version__ = "1.0.0"
__all__ = ["Config", "create_app"]
