"""
EventPublisherImpl
設計書の EventPublisher 仕様に基づくインメモリ実装
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from infrastructure.events.event_publisher import EventPublisher
from domain.events.base_domain_event import DomainEvent


class PublishStatus:
    """イベント発行状況"""

    def __init__(self, event_id: str, status: str, published_at: datetime):
        self.event_id = event_id
        self.status = status  # "PUBLISHED", "FAILED", "PENDING"
        self.published_at = published_at


class EventPublisherImpl(EventPublisher):
    """イベント発行のインメモリ実装"""

    def __init__(self, logger: logging.Logger = None):
        """EventPublisherImpl を初期化"""
        self.logger = logger or logging.getLogger(__name__)
        self._published_events: List[Dict[str, Any]] = []  # 発行済みイベントの履歴
        self._publish_status: Dict[str, PublishStatus] = {}  # 発行状況管理

    async def publish(self, event: DomainEvent) -> None:
        """
        単一イベント発行
        事前条件: eventは有効なDomainEventインスタンスである
        事後条件: イベントが配信対象のサブスクライバーに配信される
        """
        try:
            # イベントの妥当性チェック
            if not event:
                raise ValueError("イベントが指定されていません")

            if not hasattr(event, 'event_id') or not event.event_id:
                raise ValueError("イベントIDが不正です")

            # イベント発行処理（インメモリ実装）
            event_data = event.to_dict()
            self._published_events.append({
                **event_data,
                "published_at": datetime.now().isoformat(),
                "publisher": "EventPublisherImpl",
                "delivery_status": "DELIVERED"  # インメモリ実装では即座に配信完了
            })

            # 発行状況の記録
            self._publish_status[event.event_id] = PublishStatus(
                event_id=event.event_id,
                status="PUBLISHED",
                published_at=datetime.now()
            )

            # ログ出力
            self.logger.info(
                f"Event published successfully: {event.get_event_type()}, "
                f"event_id: {event.event_id}, "
                f"aggregate_id: {event.aggregate_id}"
            )

            # Unit2への連携データ送信（シミュレーション）
            await self._send_to_unit2(event)

        except Exception as e:
            # 発行失敗の記録
            if event and hasattr(event, 'event_id'):
                self._publish_status[event.event_id] = PublishStatus(
                    event_id=event.event_id,
                    status="FAILED",
                    published_at=datetime.now()
                )

            self.logger.error(f"Event publishing failed: {str(e)}")
            raise

    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """複数イベント一括発行"""
        try:
            if not events:
                return

            for event in events:
                await self.publish(event)

            self.logger.info(f"Batch events published successfully: {len(events)} events")

        except Exception as e:
            self.logger.error(f"Batch event publishing failed: {str(e)}")
            raise

    async def get_publish_status(self, event_id: str) -> PublishStatus:
        """発行状況の確認"""
        if event_id not in self._publish_status:
            raise ValueError(f"イベントが見つかりません: {event_id}")

        return self._publish_status[event_id]

    async def _send_to_unit2(self, event: DomainEvent) -> None:
        """Unit2への連携データ送信（シミュレーション）"""
        try:
            # TaskCreatedEventの場合、TaskDataInterface形式で送信
            if event.get_event_type() == "TaskCreated":
                unit2_data = event.to_task_data_interface()
                self.logger.info(
                    f"Sent to Unit2 (TaskDataInterface): {unit2_data}"
                )
            else:
                # その他のイベントタイプの処理
                self.logger.info(
                    f"Event sent to Unit2: {event.get_event_type()}, "
                    f"event_id: {event.event_id}"
                )

        except Exception as e:
            self.logger.warning(f"Failed to send event to Unit2: {str(e)}")
            # Unit2への送信失敗は全体の処理を停止させない

    # デバッグ・監視用メソッド
    def get_published_events(self) -> List[Dict[str, Any]]:
        """発行済みイベント一覧を取得（デバッグ用）"""
        return self._published_events.copy()

    def get_published_events_count(self) -> int:
        """発行済みイベント数を取得"""
        return len(self._published_events)

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """イベントタイプ別の発行済みイベントを取得"""
        return [
            event for event in self._published_events
            if event.get("event_type") == event_type
        ]

    def clear_published_events(self) -> None:
        """発行済みイベントをクリア（テスト用）"""
        self._published_events.clear()
        self._publish_status.clear()

    def get_publisher_stats(self) -> Dict[str, Any]:
        """発行統計情報を取得（監視用）"""
        total_events = len(self._published_events)
        successful_events = sum(
            1 for status in self._publish_status.values()
            if status.status == "PUBLISHED"
        )
        failed_events = sum(
            1 for status in self._publish_status.values()
            if status.status == "FAILED"
        )

        return {
            "total_events": total_events,
            "successful_events": successful_events,
            "failed_events": failed_events,
            "success_rate": successful_events / total_events if total_events > 0 else 0,
            "publisher_type": "in_memory",
            "version": "1.0"
        }