"""
TaskFactory
設計書の TaskFactory 仕様に基づく実装
複雑なTask生成ロジックの集約
"""
from domain.entities.task import Task
from domain.value_objects.task_name import TaskName
from domain.value_objects.task_id import TaskId
from domain.value_objects.task_status import TaskStatus
from domain.value_objects.datetime_value import CreatedAt, UpdatedAt
from domain.events.task_created_event import TaskCreatedEvent
from domain.exceptions.domain_exceptions import TaskFactoryException


class TaskCreationResult:
    """タスク作成処理の結果を格納"""

    def __init__(
        self,
        task: Task,
        event: TaskCreatedEvent,
        success: bool = True
    ):
        """
        タスク作成結果を作成
        属性:
        - task: 作成されたタスク
        - event: 生成されたイベント
        - success: 成功フラグ
        """
        self.task = task
        self.event = event
        self.success = success
        self.created_at = task.created_at.value

    def is_success(self) -> bool:
        """成功/失敗判定"""
        return self.success

    def get_task(self) -> Task:
        """作成されたタスクを取得"""
        return self.task

    def get_event(self) -> TaskCreatedEvent:
        """生成されたイベントを取得"""
        return self.event


class TaskFactory:
    """複雑なTask生成ロジックの集約"""

    @staticmethod
    def create_task(
        task_name: str,
        user_id: str = "system"
    ) -> Task:
        """
        バリデーション付きTask作成
        設計書の createTask() 仕様に対応

        処理フロー:
        1. TaskNameの作成とバリデーション
        2. TaskIdの自動生成
        3. TaskStatusのデフォルト値設定（"未完了"）
        4. CreatedAt、UpdatedAtの現在日時設定
        5. 不変条件の検証
        6. Taskエンティティの生成

        事前条件: task_nameが指定されている
        事後条件: 有効なTaskエンティティが作成される
        """
        try:
            # 1. TaskNameの作成とバリデーション（BR-001, BR-004, BR-005）
            validated_task_name = TaskName(task_name)

            # 2. Taskエンティティの作成
            task = Task.create(validated_task_name, user_id)

            return task

        except Exception as e:
            raise TaskFactoryException(f"タスク作成に失敗しました: {str(e)}")

    @staticmethod
    def create_task_with_event(
        task_name: str,
        user_id: str = "system"
    ) -> TaskCreationResult:
        """
        イベント生成付きタスク作成
        設計書の createTaskWithEvent() 仕様に対応

        目的: ドメインイベント付きでタスクを作成
        戻り値: TaskCreationResult（Task + TaskCreatedEvent）
        """
        try:
            # タスク作成
            task = TaskFactory.create_task(task_name, user_id)

            # ドメインイベント生成
            event = task.create_domain_event(user_id)

            return TaskCreationResult(
                task=task,
                event=event,
                success=True
            )

        except Exception as e:
            raise TaskFactoryException(f"イベント付きタスク作成に失敗しました: {str(e)}")

    @staticmethod
    def create_task_with_defaults(
        task_name: str,
        user_id: str = "system",
        apply_security_defaults: bool = True
    ) -> Task:
        """
        デフォルト値適用タスク作成
        設計書のデフォルト値設定機能に対応

        機能:
        - 必須でない項目のデフォルト値またはNULL設定（BR-006）
        - セキュリティ設定の適用
        """
        try:
            # 基本的なタスク作成
            task = TaskFactory.create_task(task_name, user_id)

            # セキュリティデフォルト設定の適用
            if apply_security_defaults:
                # 将来的な拡張: セキュリティ関連のデフォルト設定
                # 例: 機密レベル、アクセス権限などの設定
                pass

            return task

        except Exception as e:
            raise TaskFactoryException(f"デフォルト値適用タスク作成に失敗しました: {str(e)}")

    @staticmethod
    def restore_task(
        task_id: str,
        task_name: str,
        status: str,
        created_at_iso: str,
        updated_at_iso: str
    ) -> Task:
        """
        永続化データからのタスク復元
        インフラ層からの呼び出し用

        用途: データベースやストレージからTaskエンティティを復元
        """
        try:
            from datetime import datetime

            # 値オブジェクトの復元
            restored_task_id = TaskId(task_id)
            restored_task_name = TaskName(task_name)
            restored_status = TaskStatus(status)
            restored_created_at = CreatedAt(datetime.fromisoformat(created_at_iso))
            restored_updated_at = UpdatedAt(datetime.fromisoformat(updated_at_iso))

            # Taskエンティティの復元
            task = Task(
                task_id=restored_task_id,
                task_name=restored_task_name,
                status=restored_status,
                created_at=restored_created_at,
                updated_at=restored_updated_at
            )

            return task

        except Exception as e:
            raise TaskFactoryException(f"タスク復元に失敗しました: {str(e)}")

    @staticmethod
    def validate_task_creation_prerequisites(
        task_name: str,
        user_id: str
    ) -> bool:
        """
        タスク作成の事前条件確認
        エラーハンドリング・バリデーション支援用

        確認項目:
        - タスク名の基本的な妥当性
        - ユーザーIDの妥当性
        """
        try:
            # 基本的な null チェック
            if not task_name or not user_id:
                return False

            # タスク名の基本的な長さチェック
            if len(task_name.strip()) == 0 or len(task_name.strip()) > 100:
                return False

            # ユーザーIDの基本的な形式チェック
            if len(user_id.strip()) == 0:
                return False

            return True

        except Exception:
            return False