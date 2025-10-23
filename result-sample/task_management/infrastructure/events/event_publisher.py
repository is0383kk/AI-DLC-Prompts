"""
EventPublisherインターフェース
設計書のイベント発行契約に基づく実装
"""
from abc import ABC, abstractmethod
from typing import List
from domain.events.base_domain_event import DomainEvent


class EventPublisher(ABC):
    """イベント発行インターフェース"""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        単一イベント発行
        事前条件: eventは有効なDomainEventインスタンスである
        事後条件: イベントが配信対象のサブスクライバーに配信される
        """
        pass

    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """
        複数イベント一括発行
        """
        pass