"""
TaskId値オブジェクト
設計書の TaskId 仕様に基づく実装
"""
import uuid
from typing import Any
from domain.exceptions.domain_exceptions import TaskValidationException


class TaskId:
    """タスクID値オブジェクト（UUID形式）"""

    def __init__(self, value: str):
        """
        TaskId を作成
        制約:
        - null不可
        - 空文字不可
        - UUID形式であること
        """
        if not value:
            raise TaskValidationException("TaskId は null でなく、空文字でもありません")

        # UUID形式の妥当性チェック
        try:
            uuid.UUID(value)
        except ValueError:
            raise TaskValidationException(f"TaskId は UUID 形式である必要があります: {value}")

        self._value = value

    @classmethod
    def generate(cls) -> 'TaskId':
        """新しいUUIDを生成してTaskIdを作成"""
        return cls(str(uuid.uuid4()))

    @property
    def value(self) -> str:
        """値を取得"""
        return self._value

    def __eq__(self, other: Any) -> bool:
        """等価性比較"""
        if not isinstance(other, TaskId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """ハッシュ値"""
        return hash(self._value)

    def __str__(self) -> str:
        """文字列表現への変換"""
        return self._value

    def __repr__(self) -> str:
        return f"TaskId('{self._value}')"