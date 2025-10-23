"""
ドメインイベント基底クラス
設計書のドメインイベント仕様に基づく実装
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
import uuid


class DomainEvent(ABC):
    """ドメインイベントの基底クラス"""

    def __init__(self, aggregate_id: str, aggregate_type: str):
        self.event_id = str(uuid.uuid4())
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.occurred_at = datetime.now()
        self.version = 1

    @abstractmethod
    def get_event_type(self) -> str:
        """イベントタイプを取得"""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換"""
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """イベントメタデータを取得"""
        return {
            "event_id": self.event_id,
            "event_type": self.get_event_type(),
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "occurred_at": self.occurred_at.isoformat(),
            "version": self.version
        }