"""数据模型"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Event:
    """游戏事件模型"""

    event_time: str
    event_name: str
    user_id: str
    server: str
    device: str
    level: str
    pay_amount: float = 0
    duration: int = 0
    properties: Optional[Dict[str, Any]] = None

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        import json

        data = {
            "event_time": self.event_time,
            "event_name": self.event_name,
            "user_id": self.user_id,
            "server": self.server,
            "device": self.device,
            "level": self.level,
            "pay_amount": self.pay_amount,
            "duration": self.duration,
            "properties": self.properties or {},
        }
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """从字典创建事件"""
        return cls(
            event_time=data["event_time"],
            event_name=data["event_name"],
            user_id=data["user_id"],
            server=data["server"],
            device=data["device"],
            level=data.get("level", ""),
            pay_amount=float(data.get("pay_amount", 0)),
            duration=int(data.get("duration", 0)),
            properties=data.get("properties", {}),
        )
