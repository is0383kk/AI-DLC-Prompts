"""
セキュリティチェック結果値オブジェクト
設計書の SecurityCheckResult, SanitizedInput 仕様に基づく実装
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum


class SecurityRiskLevel(Enum):
    """セキュリティリスクレベル"""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityAction(Enum):
    """推奨されるセキュリティアクション"""
    ALLOW = "ALLOW"
    SANITIZE = "SANITIZE"
    REJECT = "REJECT"
    AUDIT = "AUDIT"


class SecurityThreat:
    """検出されたセキュリティ脅威"""

    def __init__(
        self,
        threat_type: str,
        description: str,
        risk_level: SecurityRiskLevel
    ):
        self.threat_type = threat_type
        self.description = description
        self.risk_level = risk_level

    def __repr__(self) -> str:
        return f"SecurityThreat({self.threat_type}: {self.risk_level.value})"


class Modification:
    """サニタイゼーション時の変更履歴"""

    def __init__(
        self,
        original: str,
        modified: str,
        reason: str
    ):
        self.original = original
        self.modified = modified
        self.reason = reason

    def __repr__(self) -> str:
        return f"Modification('{self.original}' -> '{self.modified}': {self.reason})"


class SanitizedInput:
    """サニタイズ済み入力結果"""

    def __init__(
        self,
        clean_input: str,
        modifications: Optional[List[Modification]] = None,
        risk_level: SecurityRiskLevel = SecurityRiskLevel.NONE
    ):
        """
        サニタイズ結果を作成
        戻り値:
        - clean_input: サニタイズ済み入力
        - modifications: 変更履歴
        - risk_level: リスクレベル
        """
        self.clean_input = clean_input
        self.modifications = modifications or []
        self.risk_level = risk_level
        self.sanitized_at = datetime.now()

    def has_modifications(self) -> bool:
        """変更が行われたかチェック"""
        return len(self.modifications) > 0

    def __repr__(self) -> str:
        mod_count = len(self.modifications)
        return f"SanitizedInput('{self.clean_input}', {mod_count} modifications, {self.risk_level.value})"


class SecurityCheckResult:
    """セキュリティ制約の確認結果"""

    def __init__(
        self,
        is_passed: bool,
        detected_threats: Optional[List[SecurityThreat]] = None,
        recommended_action: SecurityAction = SecurityAction.ALLOW
    ):
        """
        セキュリティチェック結果を作成
        戻り値:
        - is_passed: チェック通過フラグ
        - detected_threats: 検出された脅威
        - recommended_action: 推奨アクション
        """
        self.is_passed = is_passed
        self.detected_threats = detected_threats or []
        self.recommended_action = recommended_action
        self.checked_at = datetime.now()

    def get_critical_threats(self) -> List[SecurityThreat]:
        """クリティカルな脅威のみを取得"""
        return [
            threat for threat in self.detected_threats
            if threat.risk_level == SecurityRiskLevel.CRITICAL
        ]

    def has_high_risk_threats(self) -> bool:
        """高リスクまたはクリティカルな脅威があるかチェック"""
        return any(
            threat.risk_level in [SecurityRiskLevel.HIGH, SecurityRiskLevel.CRITICAL]
            for threat in self.detected_threats
        )

    def __repr__(self) -> str:
        status = "Passed" if self.is_passed else f"Failed ({len(self.detected_threats)} threats)"
        return f"SecurityCheckResult({status}, {self.recommended_action.value})"