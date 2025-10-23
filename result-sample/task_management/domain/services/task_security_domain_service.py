"""
TaskSecurityDomainService
設計書の TaskSecurityDomainService 仕様に基づく実装
セキュリティ制約チェック・サニタイゼーション（BR-005）対応
"""
import html
import re
from enum import Enum
from typing import List
from domain.value_objects.security_result import (
    SanitizedInput,
    SecurityCheckResult,
    SecurityThreat,
    SecurityRiskLevel,
    SecurityAction,
    Modification
)
from domain.services.task_validation_domain_service import TaskCreationContext


class SanitizationPolicy(Enum):
    """サニタイゼーションポリシー"""
    STRICT = "STRICT"      # 厳格な制限（デフォルト）
    MODERATE = "MODERATE"  # 一般的な制限
    LENIENT = "LENIENT"    # 緩やかな制限


class TaskSecurityDomainService:
    """タスク作成時のセキュリティ処理"""

    def __init__(self, policy: SanitizationPolicy = SanitizationPolicy.STRICT):
        self.policy = policy

    def sanitize_task_input(
        self,
        raw_input: str,
        sanitization_policy: SanitizationPolicy = None
    ) -> SanitizedInput:
        """
        タスク入力データのサニタイゼーション（BR-005）

        処理内容:
        1. HTMLタグの除去/エスケープ
        2. スクリプトタグの無害化
        3. 特殊文字のエスケープ
        4. ホワイトリストベースのフィルタリング
        5. 長さ制限の適用
        """
        if sanitization_policy is None:
            sanitization_policy = self.policy

        modifications: List[Modification] = []
        risk_level = SecurityRiskLevel.NONE
        clean_input = raw_input

        # 1. HTMLタグの除去/エスケープ
        clean_input, html_modifications = self._sanitize_html(clean_input)
        modifications.extend(html_modifications)

        # 2. スクリプトタグの無害化
        clean_input, script_modifications = self._sanitize_scripts(clean_input)
        modifications.extend(script_modifications)

        # 3. 特殊文字のエスケープ
        clean_input, special_modifications = self._sanitize_special_chars(clean_input, sanitization_policy)
        modifications.extend(special_modifications)

        # 4. ホワイトリストベースのフィルタリング
        clean_input, whitelist_modifications = self._apply_whitelist_filter(clean_input, sanitization_policy)
        modifications.extend(whitelist_modifications)

        # 5. 長さ制限の適用
        clean_input, length_modifications = self._apply_length_limit(clean_input)
        modifications.extend(length_modifications)

        # リスクレベルの判定
        if modifications:
            risk_level = self._calculate_risk_level(modifications)

        return SanitizedInput(
            clean_input=clean_input,
            modifications=modifications,
            risk_level=risk_level
        )

    def check_security_constraints(
        self,
        input_text: str,
        context: TaskCreationContext
    ) -> SecurityCheckResult:
        """
        セキュリティ制約の確認

        チェック項目:
        1. 悪意のあるペイロードの検出
        2. 異常な文字パターンの識別
        3. 大量データ攻撃の防止
        4. 権限ベースの制約チェック
        """
        detected_threats: List[SecurityThreat] = []

        # 1. 悪意のあるペイロードの検出
        detected_threats.extend(self._detect_malicious_payloads(input_text))

        # 2. 異常な文字パターンの識別
        detected_threats.extend(self._detect_abnormal_patterns(input_text))

        # 3. 大量データ攻撃の防止
        detected_threats.extend(self._detect_data_attacks(input_text))

        # 4. 権限ベースの制約チェック
        detected_threats.extend(self._check_permission_constraints(input_text, context))

        # 結果の判定
        is_passed = len(detected_threats) == 0
        recommended_action = self._determine_recommended_action(detected_threats)

        return SecurityCheckResult(
            is_passed=is_passed,
            detected_threats=detected_threats,
            recommended_action=recommended_action
        )

    def _sanitize_html(self, input_text: str) -> tuple[str, List[Modification]]:
        """HTMLタグの除去/エスケープ"""
        modifications: List[Modification] = []
        original = input_text

        # HTMLエスケープ
        sanitized = html.escape(input_text)

        if sanitized != original:
            modifications.append(Modification(
                original=original,
                modified=sanitized,
                reason="HTMLエスケープ処理"
            ))

        return sanitized, modifications

    def _sanitize_scripts(self, input_text: str) -> tuple[str, List[Modification]]:
        """スクリプトタグの無害化"""
        modifications: List[Modification] = []
        original = input_text
        sanitized = input_text

        # 危険なスクリプトパターンの除去
        dangerous_patterns = [
            (r'<script[^>]*>.*?</script>', ''),
            (r'javascript:', 'text:'),
            (r'on\w+\s*=\s*["\'][^"\']*["\']', ''),
            (r'<iframe[^>]*>.*?</iframe>', ''),
        ]

        for pattern, replacement in dangerous_patterns:
            new_sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE | re.DOTALL)
            if new_sanitized != sanitized:
                modifications.append(Modification(
                    original=sanitized,
                    modified=new_sanitized,
                    reason=f"危険なスクリプトパターンの除去: {pattern}"
                ))
                sanitized = new_sanitized

        return sanitized, modifications

    def _sanitize_special_chars(self, input_text: str, policy: SanitizationPolicy) -> tuple[str, List[Modification]]:
        """特殊文字のエスケープ"""
        modifications: List[Modification] = []
        sanitized = input_text

        if policy == SanitizationPolicy.STRICT:
            # 厳格な制限: 基本的な文字のみ許可
            allowed_pattern = r'[^a-zA-Z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\s\.\-_,!?()（）]'
            cleaned = re.sub(allowed_pattern, '', sanitized)
            if cleaned != sanitized:
                modifications.append(Modification(
                    original=sanitized,
                    modified=cleaned,
                    reason="厳格な文字制限適用"
                ))
                sanitized = cleaned

        return sanitized, modifications

    def _apply_whitelist_filter(self, input_text: str, policy: SanitizationPolicy) -> tuple[str, List[Modification]]:
        """ホワイトリストベースのフィルタリング"""
        modifications: List[Modification] = []
        # 現在の実装では特別な処理なし（将来拡張用）
        return input_text, modifications

    def _apply_length_limit(self, input_text: str) -> tuple[str, List[Modification]]:
        """長さ制限の適用"""
        modifications: List[Modification] = []
        MAX_LENGTH = 100

        if len(input_text) > MAX_LENGTH:
            truncated = input_text[:MAX_LENGTH]
            modifications.append(Modification(
                original=input_text,
                modified=truncated,
                reason=f"長さ制限適用（{MAX_LENGTH}文字まで）"
            ))
            return truncated, modifications

        return input_text, modifications

    def _calculate_risk_level(self, modifications: List[Modification]) -> SecurityRiskLevel:
        """リスクレベルの計算"""
        if not modifications:
            return SecurityRiskLevel.NONE

        # 変更の内容に基づいてリスクレベルを判定
        risk_keywords = ['スクリプト', 'HTML', '危険な']
        high_risk_count = sum(1 for mod in modifications if any(keyword in mod.reason for keyword in risk_keywords))

        if high_risk_count > 2:
            return SecurityRiskLevel.HIGH
        elif high_risk_count > 0:
            return SecurityRiskLevel.MEDIUM
        elif len(modifications) > 3:
            return SecurityRiskLevel.MEDIUM
        else:
            return SecurityRiskLevel.LOW

    def _detect_malicious_payloads(self, input_text: str) -> List[SecurityThreat]:
        """悪意のあるペイロードの検出"""
        threats: List[SecurityThreat] = []

        # XSS ペイロード検出
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'alert\s*\(',
            r'eval\s*\(',
        ]

        for pattern in xss_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(SecurityThreat(
                    threat_type="XSS",
                    description="XSS攻撃パターンが検出されました",
                    risk_level=SecurityRiskLevel.HIGH
                ))
                break

        # SQL インジェクション検出
        sql_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"';",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(SecurityThreat(
                    threat_type="SQL_INJECTION",
                    description="SQLインジェクション攻撃パターンが検出されました",
                    risk_level=SecurityRiskLevel.CRITICAL
                ))
                break

        return threats

    def _detect_abnormal_patterns(self, input_text: str) -> List[SecurityThreat]:
        """異常な文字パターンの識別"""
        threats: List[SecurityThreat] = []

        # 異常に長い文字列
        if len(input_text) > 1000:
            threats.append(SecurityThreat(
                threat_type="ABNORMAL_LENGTH",
                description="異常に長い入力が検出されました",
                risk_level=SecurityRiskLevel.MEDIUM
            ))

        # 制御文字の検出
        if any(ord(c) < 32 and c not in '\t\n\r' for c in input_text):
            threats.append(SecurityThreat(
                threat_type="CONTROL_CHARS",
                description="制御文字が検出されました",
                risk_level=SecurityRiskLevel.LOW
            ))

        return threats

    def _detect_data_attacks(self, input_text: str) -> List[SecurityThreat]:
        """大量データ攻撃の防止"""
        threats: List[SecurityThreat] = []

        # 繰り返しパターンの検出
        if len(set(input_text)) < len(input_text) * 0.1 and len(input_text) > 50:
            threats.append(SecurityThreat(
                threat_type="REPETITIVE_DATA",
                description="繰り返しデータパターンが検出されました",
                risk_level=SecurityRiskLevel.LOW
            ))

        return threats

    def _check_permission_constraints(self, input_text: str, context: TaskCreationContext) -> List[SecurityThreat]:
        """権限ベースの制約チェック"""
        threats: List[SecurityThreat] = []

        # システム関連キーワードの使用制限（一般ユーザー向け）
        if context.user_id != "admin" and context.user_id != "system":
            admin_keywords = ["admin", "root", "system", "config"]
            input_lower = input_text.lower()
            for keyword in admin_keywords:
                if keyword in input_lower:
                    threats.append(SecurityThreat(
                        threat_type="PRIVILEGE_ESCALATION",
                        description=f"システム管理者用キーワード「{keyword}」の使用が制限されています",
                        risk_level=SecurityRiskLevel.MEDIUM
                    ))
                    break

        return threats

    def _determine_recommended_action(self, threats: List[SecurityThreat]) -> SecurityAction:
        """推奨アクションの決定"""
        if not threats:
            return SecurityAction.ALLOW

        # 最高リスクレベルに基づいて判定
        max_risk = max(threat.risk_level for threat in threats)

        if max_risk == SecurityRiskLevel.CRITICAL:
            return SecurityAction.REJECT
        elif max_risk == SecurityRiskLevel.HIGH:
            return SecurityAction.SANITIZE
        elif max_risk == SecurityRiskLevel.MEDIUM:
            return SecurityAction.AUDIT
        else:
            return SecurityAction.ALLOW