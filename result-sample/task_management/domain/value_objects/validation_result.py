"""
バリデーション結果値オブジェクト
設計書の ValidationResult 仕様に基づく実装
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum


class ValidationSeverity(Enum):
    """バリデーション違反の重要度"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ValidationViolation:
    """個別のバリデーション違反情報"""

    def __init__(
        self,
        rule_id: str,
        message: str,
        severity: ValidationSeverity,
        field_name: str
    ):
        """
        バリデーション違反を作成
        制約:
        - すべての属性がnull不可
        - messageはユーザーフレンドリーである
        """
        if not all([rule_id, message, field_name]):
            raise ValueError("すべての属性が必須です")

        self.rule_id = rule_id
        self.message = message
        self.severity = severity
        self.field_name = field_name

    def __repr__(self) -> str:
        return f"ValidationViolation({self.rule_id}: {self.message})"


class ValidationResult:
    """バリデーション結果の詳細情報"""

    def __init__(
        self,
        is_valid: bool,
        violations: Optional[List[ValidationViolation]] = None
    ):
        """
        バリデーション結果を作成
        制約:
        - is_valid=falseの場合、violationsが空でない
        - validated_atがnull不可
        """
        self.is_valid = is_valid
        self.violations = violations or []
        self.validated_at = datetime.now()

        # 制約チェック
        if not is_valid and not self.violations:
            raise ValueError("バリデーション失敗時は違反情報が必要です")

    def get_error_messages(self) -> List[str]:
        """エラーメッセージのリストを取得"""
        return [violation.message for violation in self.violations]

    def get_violations_by_severity(self, severity: ValidationSeverity) -> List[ValidationViolation]:
        """重要度別の違反フィルタリング"""
        return [v for v in self.violations if v.severity == severity]

    def has_critical_violations(self) -> bool:
        """クリティカルな違反があるかチェック"""
        return any(v.severity == ValidationSeverity.CRITICAL for v in self.violations)

    def __repr__(self) -> str:
        status = "Valid" if self.is_valid else f"Invalid ({len(self.violations)} violations)"
        return f"ValidationResult({status})"