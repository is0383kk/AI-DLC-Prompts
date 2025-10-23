"""
ドメイン例外クラス階層
設計書の例外階層に基づく実装
"""
from typing import List, Optional


class TaskDomainException(Exception):
    """ドメイン例外の基底クラス"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class TaskValidationException(TaskDomainException):
    """バリデーション例外"""

    def __init__(self, message: str, violations: Optional[List[str]] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.violations = violations or []


class TaskNameValidationException(TaskValidationException):
    """タスク名バリデーション例外"""
    pass


class TaskContextValidationException(TaskValidationException):
    """コンテキストバリデーション例外"""
    pass


class TaskBusinessRuleViolationException(TaskValidationException):
    """ビジネスルール違反例外"""
    pass


class TaskSecurityException(TaskDomainException):
    """セキュリティ例外"""

    def __init__(self, message: str, threat_type: Optional[str] = None):
        super().__init__(message, "SECURITY_ERROR")
        self.threat_type = threat_type


class TaskInputSanitizationException(TaskSecurityException):
    """入力サニタイゼーション例外"""
    pass


class TaskSecurityConstraintViolationException(TaskSecurityException):
    """セキュリティ制約違反例外"""
    pass


class TaskSecurityThreatDetectedException(TaskSecurityException):
    """セキュリティ脅威検出例外"""
    pass


class TaskCreationException(TaskDomainException):
    """タスク作成例外"""

    def __init__(self, message: str):
        super().__init__(message, "CREATION_ERROR")


class TaskFactoryException(TaskCreationException):
    """ファクトリ例外"""
    pass


class TaskEventGenerationException(TaskCreationException):
    """イベント生成例外"""
    pass