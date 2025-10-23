"""
TaskCreatedEvent
設計書の TaskCreatedEvent 仕様に基づく実装
"""
from datetime import datetime
from typing import Dict, Any
from .base_domain_event import DomainEvent


class TaskCreatedEvent(DomainEvent):
    """タスク作成完了イベント"""

    def __init__(
        self,
        task_id: str,
        task_name: str,
        user_id: str,
        created_at: datetime
    ):
        """
        TaskCreatedEvent を作成
        属性:
        - task_id: 作成されたタスクID
        - task_name: 作成されたタスク名
        - user_id: 作成者ID
        - created_at: タスク作成日時
        """
        super().__init__(aggregate_id=task_id, aggregate_type="Task")
        self.task_id = task_id
        self.task_name = task_name
        self.user_id = user_id
        self.created_at = created_at

    def get_event_type(self) -> str:
        """イベントタイプを取得"""
        return "TaskCreated"

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換（他ユニットとの連携用）"""
        return {
            **self.get_metadata(),
            "task_id": self.task_id,
            "task_name": self.task_name,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
        }

    def to_task_data_interface(self) -> Dict[str, Any]:
        """
        TaskDataInterface形式への変換
        Unit2との連携データ形式
        """
        return {
            "taskId": self.task_id,
            "taskName": self.task_name,
            "createdAt": self.created_at.isoformat(),
            "status": "未完了",
            "metadata": {
                "version": "1.0.0",
                "source": "unit1-task-creation",
                "lastModified": self.occurred_at.isoformat()
            }
        }