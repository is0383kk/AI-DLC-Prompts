"""
TaskStatus値オブジェクト
設計書の TaskStatus 仕様に基づく実装
"""
from enum import Enum
from typing import Any
from domain.exceptions.domain_exceptions import TaskValidationException


class TaskStatusEnum(Enum):
    """タスクステータス列挙型"""
    PENDING = "未完了"
    COMPLETED = "完了"
    ON_HOLD = "保留"


class TaskStatus:
    """タスクステータス値オブジェクト"""

    def __init__(self, value: str = None):
        """
        TaskStatus を作成
        制約:
        - 事前定義された値のみ許可
        - null不可
        """
        if value is None:
            # デフォルト値は「未完了」（設計書 BIV-001）
            self._enum_value = TaskStatusEnum.PENDING
        else:
            # 入力値から対応する列挙型を検索
            matching_status = None
            for status in TaskStatusEnum:
                if status.value == value:
                    matching_status = status
                    break

            if matching_status is None:
                valid_values = [status.value for status in TaskStatusEnum]
                raise TaskValidationException(
                    f"無効なタスクステータスです: {value}. "
                    f"有効な値: {', '.join(valid_values)}"
                )

            self._enum_value = matching_status

    @classmethod
    def pending(cls) -> 'TaskStatus':
        """未完了ステータスを作成"""
        return cls(TaskStatusEnum.PENDING.value)

    @classmethod
    def completed(cls) -> 'TaskStatus':
        """完了ステータスを作成"""
        return cls(TaskStatusEnum.COMPLETED.value)

    @classmethod
    def on_hold(cls) -> 'TaskStatus':
        """保留ステータスを作成"""
        return cls(TaskStatusEnum.ON_HOLD.value)

    @property
    def value(self) -> str:
        """値を取得"""
        return self._enum_value.value

    def is_pending(self) -> bool:
        """未完了かどうか"""
        return self._enum_value == TaskStatusEnum.PENDING

    def is_completed(self) -> bool:
        """完了かどうか"""
        return self._enum_value == TaskStatusEnum.COMPLETED

    def is_on_hold(self) -> bool:
        """保留かどうか"""
        return self._enum_value == TaskStatusEnum.ON_HOLD

    def __eq__(self, other: Any) -> bool:
        """等価性比較"""
        if not isinstance(other, TaskStatus):
            return False
        return self._enum_value == other._enum_value

    def __hash__(self) -> int:
        """ハッシュ値"""
        return hash(self._enum_value)

    def __str__(self) -> str:
        """文字列表現への変換"""
        return self._enum_value.value

    def __repr__(self) -> str:
        return f"TaskStatus('{self._enum_value.value}')"