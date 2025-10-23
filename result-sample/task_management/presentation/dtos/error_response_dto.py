"""
ErrorResponseDTO
設計書の ErrorResponseDTO 仕様に基づく実装
HTTP エラーレスポンス用のDTO
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any


class ErrorDetailDTO(BaseModel):
    """エラー詳細情報用DTO"""

    field: str = Field(
        ...,
        title="フィールド名",
        description="エラーが発生したフィールド名",
        example="task_name"
    )

    code: str = Field(
        ...,
        title="エラーコード",
        description="エラーの種類を表すコード",
        example="VALIDATION_FAILED"
    )

    message: str = Field(
        ...,
        title="エラーメッセージ",
        description="ユーザー向けのエラーメッセージ",
        example="タスク名は必須です"
    )

    value: Optional[Any] = Field(
        default=None,
        title="エラー値",
        description="エラーの原因となった値",
        example=""
    )


class ErrorResponseDTO(BaseModel):
    """エラーレスポンス用DTO"""

    error_code: str = Field(
        ...,
        title="エラーコード",
        description="エラーの分類コード",
        example="VALIDATION_ERROR"
    )

    error_message: str = Field(
        ...,
        title="エラーメッセージ",
        description="エラーの概要メッセージ",
        example="入力データに問題があります"
    )

    details: List[ErrorDetailDTO] = Field(
        default_factory=list,
        title="詳細エラー情報",
        description="エラーの詳細情報リスト"
    )

    timestamp: datetime = Field(
        ...,
        title="エラー発生時刻",
        description="エラーが発生した日時",
        example="2025-10-22T10:30:01.123456"
    )

    request_id: Optional[str] = Field(
        default=None,
        title="リクエストID",
        description="要求追跡用のID",
        example="req-456"
    )

    class Config:
        """Pydantic設定"""
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "error_message": "入力データに問題があります",
                "details": [
                    {
                        "field": "task_name",
                        "code": "VALIDATION_FAILED",
                        "message": "タスク名は必須です",
                        "value": ""
                    }
                ],
                "timestamp": "2025-10-22T10:30:01.123456",
                "request_id": "req-456"
            }
        }