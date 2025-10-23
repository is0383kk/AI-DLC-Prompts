"""
CreateTaskRequestDTO
設計書の CreateTaskRequestDTO 仕様に基づく実装
HTTP リクエスト用のDTO
"""
from pydantic import BaseModel, Field, validator
from typing import Optional


class CreateTaskRequestDTO(BaseModel):
    """タスク作成リクエスト用DTO"""

    task_name: str = Field(
        ...,
        title="タスク名",
        description="作成するタスクの名前",
        min_length=1,
        max_length=100,
        example="会議資料の準備"
    )

    user_id: Optional[str] = Field(
        default="system",
        title="ユーザーID",
        description="タスクを作成するユーザーのID",
        example="user-123"
    )

    @validator('task_name')
    def validate_task_name(cls, v):
        """タスク名のバリデーション"""
        if not v or not v.strip():
            raise ValueError('タスク名は必須です')

        v = v.strip()
        if len(v) > 100:
            raise ValueError('タスク名は100文字以内で入力してください')

        return v

    @validator('user_id')
    def validate_user_id(cls, v):
        """ユーザーIDのバリデーション"""
        if v and len(v.strip()) == 0:
            raise ValueError('ユーザーIDが空です')
        return v or "system"

    class Config:
        """Pydantic設定"""
        schema_extra = {
            "example": {
                "task_name": "会議資料の準備",
                "user_id": "user-123"
            }
        }