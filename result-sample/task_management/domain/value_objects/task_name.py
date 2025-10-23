"""
TaskName値オブジェクト
設計書の TaskName 仕様に基づく実装
ビジネスルール BR-001, BR-004, BR-005 対応
"""
import html
import re
from typing import Any
from domain.exceptions.domain_exceptions import (
    TaskNameValidationException,
    TaskBusinessRuleViolationException
)


class TaskName:
    """タスク名値オブジェクト"""

    MAX_LENGTH = 100

    def __init__(self, value: str):
        """
        TaskName を作成
        制約:
        - null不可（BR-001）
        - 空文字不可（BR-001）
        - 100文字以内（BR-004）
        - 特殊文字のエスケープ処理（BR-005）
        """
        if not value:
            raise TaskBusinessRuleViolationException(
                "タスク名は必須です",  # BR-001
                ["タスク名を入力してください"]
            )

        # トリミング処理
        trimmed_value = value.strip()
        if not trimmed_value:
            raise TaskBusinessRuleViolationException(
                "タスク名は必須です",  # BR-001
                ["空白のみのタスク名は無効です"]
            )

        # 文字数バリデーション（BR-004）
        if len(trimmed_value) > self.MAX_LENGTH:
            raise TaskBusinessRuleViolationException(
                f"タスク名は{self.MAX_LENGTH}文字以内で入力してください",  # BR-004
                [f"現在の文字数: {len(trimmed_value)}文字"]
            )

        # 特殊文字サニタイゼーション（BR-005）
        self._value = self._sanitize_input(trimmed_value)

    def _sanitize_input(self, value: str) -> str:
        """
        特殊文字のサニタイゼーション処理（BR-005）
        XSS攻撃の防止
        """
        # HTMLエスケープ
        sanitized = html.escape(value)

        # 危険なスクリプトパターンの除去
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>.*?</iframe>',
        ]

        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized.strip()

    @property
    def value(self) -> str:
        """値を取得"""
        return self._value

    def __eq__(self, other: Any) -> bool:
        """等価性比較"""
        if not isinstance(other, TaskName):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """ハッシュ値"""
        return hash(self._value)

    def __str__(self) -> str:
        """文字列表現への変換"""
        return self._value

    def __repr__(self) -> str:
        return f"TaskName('{self._value}')"