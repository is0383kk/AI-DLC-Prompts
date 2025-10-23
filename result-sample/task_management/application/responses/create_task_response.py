"""
CreateTaskResponse
設計書の CreateTaskResponse 仕様に基づく実装
タスク作成処理の成功結果を表現
"""
from datetime import datetime
from typing import Optional


class CreateTaskResponse:
    """タスク作成処理の成功結果を表現"""

    def __init__(
        self,
        task_id: str,
        task_name: str,
        status: str,
        created_at: datetime,
        message: str = "タスクが正常に追加されました",
        request_id: Optional[str] = None
    ):
        """
        CreateTaskResponse を作成

        制約:
        - すべての属性が非null
        - task_idはUUID形式
        - messageはユーザーフレンドリー
        """
        # 制約チェック
        if not all([task_id, task_name, status, created_at, message]):
            raise ValueError("すべての属性が必須です")

        # UUID形式チェック
        import uuid
        try:
            uuid.UUID(task_id)
        except ValueError:
            raise ValueError("task_idはUUID形式である必要があります")

        # 属性設定
        self.task_id = task_id
        self.task_name = task_name
        self.status = status
        self.created_at = created_at
        self.message = message
        self.request_id = request_id

    @classmethod
    def from_task_creation_result(cls, result, request_id: Optional[str] = None):
        """TaskCreationResult から CreateTaskResponse を作成"""
        task = result.get_task()
        return cls(
            task_id=str(task.task_id),
            task_name=str(task.task_name),
            status=str(task.status),
            created_at=task.created_at.value,
            message="タスクが正常に追加されました",  # BR-002対応
            request_id=request_id
        )

    def to_dict(self) -> dict:
        """辞書形式への変換（API レスポンス用）"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "message": self.message,
            "request_id": self.request_id
        }

    def __repr__(self) -> str:
        return (
            f"CreateTaskResponse("
            f"task_id='{self.task_id}', "
            f"task_name='{self.task_name}', "
            f"status='{self.status}', "
            f"message='{self.message}')"
        )