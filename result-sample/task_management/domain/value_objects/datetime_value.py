"""
日時値オブジェクト
設計書の CreatedAt/UpdatedAt 仕様に基づく実装
"""
from datetime import datetime
from typing import Any
from domain.exceptions.domain_exceptions import TaskValidationException


class DateTimeValue:
    """日時値オブジェクトの基底クラス"""

    def __init__(self, value: datetime = None):
        """
        日時値オブジェクトを作成
        制約:
        - null不可
        - 過去または現在の日時であること
        """
        if value is None:
            self._value = datetime.now()
        else:
            if not isinstance(value, datetime):
                raise TaskValidationException("日時値は datetime 型である必要があります")

            # 未来日時チェック（現在時刻より少し後まで許容 - 処理時間考慮）
            now = datetime.now()
            if value > now.replace(microsecond=now.microsecond + 100000):
                raise TaskValidationException("日時値は過去または現在の日時である必要があります")

            self._value = value

    @property
    def value(self) -> datetime:
        """値を取得"""
        return self._value

    def to_iso_string(self) -> str:
        """ISO8601形式の文字列に変換"""
        return self._value.isoformat()

    def __eq__(self, other: Any) -> bool:
        """等価性比較"""
        if not isinstance(other, DateTimeValue):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """ハッシュ値"""
        return hash(self._value)

    def __str__(self) -> str:
        """文字列表現への変換"""
        return self.to_iso_string()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.to_iso_string()}')"

    def __lt__(self, other: 'DateTimeValue') -> bool:
        """比較演算子（小なり）"""
        if not isinstance(other, DateTimeValue):
            return NotImplemented
        return self._value < other._value

    def __le__(self, other: 'DateTimeValue') -> bool:
        """比較演算子（小なりイコール）"""
        if not isinstance(other, DateTimeValue):
            return NotImplemented
        return self._value <= other._value

    def __gt__(self, other: 'DateTimeValue') -> bool:
        """比較演算子（大なり）"""
        if not isinstance(other, DateTimeValue):
            return NotImplemented
        return self._value > other._value

    def __ge__(self, other: 'DateTimeValue') -> bool:
        """比較演算子（大なりイコール）"""
        if not isinstance(other, DateTimeValue):
            return NotImplemented
        return self._value >= other._value


class CreatedAt(DateTimeValue):
    """作成日時値オブジェクト"""

    def __init__(self, value: datetime = None):
        super().__init__(value)


class UpdatedAt(DateTimeValue):
    """更新日時値オブジェクト"""

    def __init__(self, value: datetime = None):
        super().__init__(value)

    @classmethod
    def now(cls) -> 'UpdatedAt':
        """現在時刻で更新日時を作成"""
        return cls(datetime.now())