"""
CreateTaskCommand
設計書の CreateTaskCommand 仕様に基づく実装
タスク作成要求を表現するコマンドオブジェクト
"""
from datetime import datetime
from typing import Optional
from domain.exceptions.domain_exceptions import TaskValidationException


class ClientInfo:
    """クライアント情報"""

    def __init__(
        self,
        user_agent: str = "unknown",
        ip_address: str = "127.0.0.1",
        platform: str = "web"
    ):
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.platform = platform


class CreateTaskCommand:
    """タスク作成要求を表現するコマンドオブジェクト"""

    def __init__(
        self,
        task_name: str,
        user_id: str = "system",
        request_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        client_info: Optional[ClientInfo] = None
    ):
        """
        CreateTaskCommand を作成

        制約:
        - task_name: 必須、100文字以内、nullまたは空文字不可
        - user_id: 必須、有効なユーザーID形式
        - request_id: 必須、UUID形式
        - timestamp: 必須、現在時刻以前
        - client_info: 必須
        """
        # 構造的妥当性の検証
        self._validate_structure(task_name, user_id, request_id, timestamp)

        # 属性の設定
        self.task_name = task_name
        self.user_id = user_id
        self.request_id = request_id or self._generate_request_id()
        self.timestamp = timestamp or datetime.now()
        self.client_info = client_info or ClientInfo()

    def _validate_structure(
        self,
        task_name: str,
        user_id: str,
        request_id: Optional[str],
        timestamp: Optional[datetime]
    ) -> None:
        """構造的妥当性の検証"""

        # task_name の基本チェック
        if not task_name:
            raise TaskValidationException("タスク名は必須です")

        if not isinstance(task_name, str):
            raise TaskValidationException("タスク名は文字列である必要があります")

        # user_id の基本チェック
        if not user_id:
            raise TaskValidationException("ユーザーIDは必須です")

        if not isinstance(user_id, str):
            raise TaskValidationException("ユーザーIDは文字列である必要があります")

        # timestamp の基本チェック
        if timestamp is not None:
            if not isinstance(timestamp, datetime):
                raise TaskValidationException("タイムスタンプは datetime 型である必要があります")

            # 未来日時チェック（現在時刻より少し後まで許容）
            now = datetime.now()
            if timestamp > now.replace(microsecond=now.microsecond + 100000):
                raise TaskValidationException("タイムスタンプは現在時刻以前である必要があります")

        # request_id の基本チェック
        if request_id is not None:
            if not isinstance(request_id, str):
                raise TaskValidationException("リクエストIDは文字列である必要があります")

            # UUID形式チェック（簡易）
            import uuid
            try:
                uuid.UUID(request_id)
            except ValueError:
                raise TaskValidationException("リクエストIDはUUID形式である必要があります")

    def _generate_request_id(self) -> str:
        """リクエストIDを生成"""
        import uuid
        return str(uuid.uuid4())

    def to_creation_context(self):
        """TaskCreationContextに変換"""
        from domain.services.task_validation_domain_service import TaskCreationContext

        return TaskCreationContext(
            user_id=self.user_id,
            timestamp=self.timestamp.isoformat(),
            client_info=f"{self.client_info.platform}_{self.client_info.user_agent}",
            request_id=self.request_id
        )

    def __repr__(self) -> str:
        return (
            f"CreateTaskCommand("
            f"task_name='{self.task_name}', "
            f"user_id='{self.user_id}', "
            f"request_id='{self.request_id}', "
            f"timestamp='{self.timestamp.isoformat()}')"
        )