"""
CreateTaskErrorResponse
設計書の CreateTaskErrorResponse 仕様に基づく実装
タスク作成処理の失敗結果を表現
"""
from datetime import datetime
from typing import List, Optional, Dict, Any


class ErrorDetail:
    """詳細エラー情報"""

    def __init__(
        self,
        field: str,
        code: str,
        message: str,
        value: Optional[str] = None
    ):
        self.field = field
        self.code = code
        self.message = message
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換"""
        return {
            "field": self.field,
            "code": self.code,
            "message": self.message,
            "value": self.value
        }


class CreateTaskErrorResponse:
    """タスク作成処理の失敗結果を表現"""

    # エラーコード分類
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INFRASTRUCTURE_ERROR = "INFRASTRUCTURE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

    def __init__(
        self,
        error_code: str,
        error_message: str,
        details: Optional[List[ErrorDetail]] = None,
        timestamp: Optional[datetime] = None,
        request_id: Optional[str] = None
    ):
        """
        CreateTaskErrorResponse を作成

        制約:
        - error_codeは事前定義済みの値
        - error_messageはユーザーフレンドリー
        - detailsはトラブルシューティング用詳細情報
        """
        # 制約チェック
        valid_codes = [
            self.VALIDATION_ERROR,
            self.SECURITY_ERROR,
            self.BUSINESS_RULE_VIOLATION,
            self.INFRASTRUCTURE_ERROR,
            self.UNKNOWN_ERROR
        ]

        if error_code not in valid_codes:
            raise ValueError(f"無効なエラーコードです: {error_code}")

        if not error_message:
            raise ValueError("エラーメッセージは必須です")

        # 属性設定
        self.error_code = error_code
        self.error_message = error_message
        self.details = details or []
        self.timestamp = timestamp or datetime.now()
        self.request_id = request_id

    @classmethod
    def from_validation_exception(
        cls,
        exception,
        request_id: Optional[str] = None
    ) -> 'CreateTaskErrorResponse':
        """TaskValidationException から CreateTaskErrorResponse を作成"""
        details = []
        if hasattr(exception, 'violations') and exception.violations:
            for violation in exception.violations:
                details.append(ErrorDetail(
                    field="task_name",
                    code="VALIDATION_FAILED",
                    message=violation,
                    value=None
                ))

        return cls(
            error_code=cls.VALIDATION_ERROR,
            error_message=exception.message,
            details=details,
            request_id=request_id
        )

    @classmethod
    def from_security_exception(
        cls,
        exception,
        request_id: Optional[str] = None
    ) -> 'CreateTaskErrorResponse':
        """TaskSecurityException から CreateTaskErrorResponse を作成"""
        details = [ErrorDetail(
            field="task_name",
            code="SECURITY_THREAT",
            message="セキュリティ制約に違反する内容が検出されました",
            value=None
        )]

        return cls(
            error_code=cls.SECURITY_ERROR,
            error_message="入力データにセキュリティ上の問題があります",  # セキュリティ考慮で一般的なメッセージ
            details=details,
            request_id=request_id
        )

    @classmethod
    def from_business_rule_violation(
        cls,
        exception,
        request_id: Optional[str] = None
    ) -> 'CreateTaskErrorResponse':
        """TaskBusinessRuleViolationException から CreateTaskErrorResponse を作成"""
        details = []
        if hasattr(exception, 'violations') and exception.violations:
            for violation in exception.violations:
                details.append(ErrorDetail(
                    field="task_name",
                    code="BUSINESS_RULE_VIOLATION",
                    message=violation,
                    value=None
                ))

        return cls(
            error_code=cls.BUSINESS_RULE_VIOLATION,
            error_message=exception.message,
            details=details,
            request_id=request_id
        )

    @classmethod
    def from_infrastructure_error(
        cls,
        message: str = "一時的な問題が発生しました",
        request_id: Optional[str] = None
    ) -> 'CreateTaskErrorResponse':
        """インフラエラー用の CreateTaskErrorResponse を作成"""
        return cls(
            error_code=cls.INFRASTRUCTURE_ERROR,
            error_message=message,  # セキュリティ考慮で詳細な内部情報は隠蔽
            details=[],
            request_id=request_id
        )

    @classmethod
    def from_unknown_error(
        cls,
        request_id: Optional[str] = None
    ) -> 'CreateTaskErrorResponse':
        """不明なエラー用の CreateTaskErrorResponse を作成"""
        return cls(
            error_code=cls.UNKNOWN_ERROR,
            error_message="予期しないエラーが発生しました",
            details=[],
            request_id=request_id
        )

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換（API レスポンス用）"""
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": [detail.to_dict() for detail in self.details],
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id
        }

    def __repr__(self) -> str:
        return (
            f"CreateTaskErrorResponse("
            f"error_code='{self.error_code}', "
            f"error_message='{self.error_message}', "
            f"details_count={len(self.details)})"
        )