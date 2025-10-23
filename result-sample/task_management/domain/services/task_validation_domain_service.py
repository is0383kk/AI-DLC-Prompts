"""
TaskValidationDomainService
設計書の TaskValidationDomainService 仕様に基づく実装
ビジネスルール BR-001, BR-004, BR-005 対応
"""
import re
from typing import List
from domain.value_objects.validation_result import (
    ValidationResult,
    ValidationViolation,
    ValidationSeverity
)


class TaskCreationContext:
    """タスク作成時のコンテキスト情報"""

    def __init__(
        self,
        user_id: str = "system",
        timestamp: str = None,
        client_info: str = "web",
        request_id: str = None
    ):
        self.user_id = user_id
        self.timestamp = timestamp
        self.client_info = client_info
        self.request_id = request_id


class TaskValidationDomainService:
    """タスク作成時の高度なバリデーションロジック"""

    # 予約語リスト
    RESERVED_WORDS = [
        "admin", "system", "root", "null", "undefined",
        "script", "alert", "eval", "function"
    ]

    # 不適切なコンテンツパターン
    INAPPROPRIATE_PATTERNS = [
        r"(?i)(password|secret|token|key)\s*[:=]",
        r"(?i)(credit\s*card|social\s*security)",
        r"(?i)(hack|crack|exploit)",
    ]

    def validate_task_creation(
        self,
        task_name: str,
        context: TaskCreationContext
    ) -> ValidationResult:
        """
        タスク作成時の包括的バリデーション

        バリデーション項目:
        1. 基本バリデーション（BR-001, BR-004）
        2. セキュリティバリデーション（BR-005）
        3. ビジネスルールバリデーション
        4. コンテキストバリデーション
        """
        violations: List[ValidationViolation] = []

        # 1. 基本バリデーション
        violations.extend(self._validate_basic_rules(task_name))

        # 2. セキュリティバリデーション
        violations.extend(self._validate_security_rules(task_name))

        # 3. ビジネスルールバリデーション
        violations.extend(self._validate_business_rules(task_name))

        # 4. コンテキストバリデーション
        violations.extend(self._validate_context_rules(context))

        is_valid = len(violations) == 0
        return ValidationResult(is_valid=is_valid, violations=violations)

    def _validate_basic_rules(self, task_name: str) -> List[ValidationViolation]:
        """基本バリデーション（BR-001, BR-004）"""
        violations: List[ValidationViolation] = []

        # BR-001: null/空文字チェック
        if not task_name:
            violations.append(ValidationViolation(
                rule_id="BR-001",
                message="タスク名は必須です",
                severity=ValidationSeverity.CRITICAL,
                field_name="task_name"
            ))
            return violations  # 以降のチェックは不要

        # 空白のみチェック
        if not task_name.strip():
            violations.append(ValidationViolation(
                rule_id="BR-001",
                message="タスク名は必須です（空白のみは無効）",
                severity=ValidationSeverity.CRITICAL,
                field_name="task_name"
            ))

        # BR-004: 文字数制限チェック
        if len(task_name.strip()) > 100:
            violations.append(ValidationViolation(
                rule_id="BR-004",
                message=f"タスク名は100文字以内で入力してください（現在: {len(task_name.strip())}文字）",
                severity=ValidationSeverity.HIGH,
                field_name="task_name"
            ))

        return violations

    def _validate_security_rules(self, task_name: str) -> List[ValidationViolation]:
        """セキュリティバリデーション（BR-005）"""
        violations: List[ValidationViolation] = []

        # XSS攻撃パターン検出
        xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"eval\s*\(",
            r"alert\s*\(",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, task_name, re.IGNORECASE):
                violations.append(ValidationViolation(
                    rule_id="BR-005",
                    message="タスク名に許可されていない文字が含まれています",
                    severity=ValidationSeverity.CRITICAL,
                    field_name="task_name"
                ))
                break

        # SQLインジェクション パターン検出
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"insert\s+into",
            r"delete\s+from",
            r"update\s+set",
            r"--\s*$",
            r"';",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, task_name, re.IGNORECASE):
                violations.append(ValidationViolation(
                    rule_id="BR-005",
                    message="タスク名に許可されていない文字が含まれています",
                    severity=ValidationSeverity.CRITICAL,
                    field_name="task_name"
                ))
                break

        return violations

    def _validate_business_rules(self, task_name: str) -> List[ValidationViolation]:
        """ビジネスルールバリデーション"""
        violations: List[ValidationViolation] = []

        # 予約語チェック
        task_name_lower = task_name.lower().strip()
        for reserved_word in self.RESERVED_WORDS:
            if reserved_word in task_name_lower:
                violations.append(ValidationViolation(
                    rule_id="BR-RESERVED",
                    message=f"タスク名に予約語「{reserved_word}」は使用できません",
                    severity=ValidationSeverity.MEDIUM,
                    field_name="task_name"
                ))

        # 不適切なコンテンツフィルタ
        for pattern in self.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, task_name):
                violations.append(ValidationViolation(
                    rule_id="BR-CONTENT",
                    message="タスク名に不適切な内容が含まれている可能性があります",
                    severity=ValidationSeverity.HIGH,
                    field_name="task_name"
                ))
                break

        return violations

    def _validate_context_rules(self, context: TaskCreationContext) -> List[ValidationViolation]:
        """コンテキストバリデーション"""
        violations: List[ValidationViolation] = []

        # ユーザーID検証
        if not context.user_id:
            violations.append(ValidationViolation(
                rule_id="BR-CONTEXT-USER",
                message="ユーザーIDが必要です",
                severity=ValidationSeverity.HIGH,
                field_name="user_id"
            ))

        # レート制限チェック（簡易実装）
        # 実際の実装では外部ストレージやキャッシュを使用
        if context.user_id and context.user_id != "system":
            # 実装例: 1分間に10件まで
            # この例では常に通過（実際の制限は省略）
            pass

        return violations