"""
TaskResponseDTO
設計書の TaskResponseDTO 仕様に基づく実装
HTTP レスポンス用のDTO
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskResponseDTO(BaseModel):
    """タスク作成成功レスポンス用DTO"""

    task_id: str = Field(
        ...,
        title="タスクID",
        description="作成されたタスクの一意識別子",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    task_name: str = Field(
        ...,
        title="タスク名",
        description="作成されたタスクの名前",
        example="会議資料の準備"
    )

    status: str = Field(
        ...,
        title="ステータス",
        description="タスクの現在のステータス",
        example="未完了"
    )

    created_at: datetime = Field(
        ...,
        title="作成日時",
        description="タスクが作成された日時",
        example="2025-10-22T10:30:01.123456"
    )

    message: Optional[str] = Field(
        default="タスクが正常に追加されました",
        title="メッセージ",
        description="処理結果メッセージ",
        example="タスクが正常に追加されました"
    )

    class Config:
        """Pydantic設定"""
        schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "task_name": "会議資料の準備",
                "status": "未完了",
                "created_at": "2025-10-22T10:30:01.123456",
                "message": "タスクが正常に追加されました"
            }
        }