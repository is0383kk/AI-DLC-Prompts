"""
Task エンティティ
設計書の Task エンティティ仕様に基づく実装
集約ルート、不変条件・ビジネス不変条件対応
"""
from typing import Any
from domain.value_objects.task_id import TaskId
from domain.value_objects.task_name import TaskName
from domain.value_objects.task_status import TaskStatus
from domain.value_objects.datetime_value import CreatedAt, UpdatedAt
from domain.events.task_created_event import TaskCreatedEvent
from domain.exceptions.domain_exceptions import TaskValidationException


class Task:
    """
    Task エンティティ（集約ルート）
    責務: ユーザーが管理するタスクの基本情報と状態を保持する
    """

    def __init__(
        self,
        task_id: TaskId,
        task_name: TaskName,
        status: TaskStatus = None,
        created_at: CreatedAt = None,
        updated_at: UpdatedAt = None
    ):
        """
        Task エンティティを作成
        不変条件の検証を実行
        """
        # 必須属性の検証
        if not task_id:
            raise TaskValidationException("taskId は null でなく、かつ一意である必要があります")  # INV-001

        if not task_name:
            raise TaskValidationException("taskName は null でなく、空文字でなく、100文字以内である必要があります")  # INV-002

        # デフォルト値の設定
        if status is None:
            status = TaskStatus.pending()  # BIV-001: 初期状態「未完了」

        if created_at is None:
            created_at = CreatedAt()

        if updated_at is None:
            updated_at = UpdatedAt()

        # 不変条件の検証
        self._validate_invariants(task_id, task_name, status, created_at, updated_at)

        # 属性の設定
        self._task_id = task_id
        self._task_name = task_name
        self._status = status
        self._created_at = created_at
        self._updated_at = updated_at

    def _validate_invariants(
        self,
        task_id: TaskId,
        task_name: TaskName,
        status: TaskStatus,
        created_at: CreatedAt,
        updated_at: UpdatedAt
    ):
        """
        不変条件の検証
        INV-001～INV-005, BIV-001～BIV-003
        """
        # INV-001: taskId は null でなく、かつ一意である
        if not task_id:
            raise TaskValidationException("INV-001: taskId は null でなく、かつ一意である必要があります")

        # INV-002: taskName は null でなく、空文字でなく、100文字以内である
        if not task_name:
            raise TaskValidationException("INV-002: taskName は null でなく、空文字でなく、100文字以内である必要があります")

        # INV-003: status は定義済みの値のいずれかである
        if not status:
            raise TaskValidationException("INV-003: status は定義済みの値のいずれかである必要があります")

        # INV-004: createdAt は updatedAt より前または同じ日時である
        if created_at and updated_at and created_at > updated_at:
            raise TaskValidationException("INV-004: createdAt は updatedAt より前または同じ日時である必要があります")

        # INV-005: すべての属性がnullでない
        if not all([task_id, task_name, status, created_at, updated_at]):
            raise TaskValidationException("INV-005: すべての属性がnullでない必要があります")

    @classmethod
    def create(cls, task_name: TaskName, user_id: str = "system") -> 'Task':
        """
        新しいTaskエンティティを作成
        設計書の作成時の振る舞いに対応
        """
        # TaskIdの自動生成
        task_id = TaskId.generate()

        # TaskStatusのデフォルト値設定（「未完了」）
        status = TaskStatus.pending()

        # 日時の現在日時設定
        now_created = CreatedAt()
        now_updated = UpdatedAt()

        # Taskエンティティの生成
        task = cls(
            task_id=task_id,
            task_name=task_name,
            status=status,
            created_at=now_created,
            updated_at=now_updated
        )

        return task

    def update_task_name(self, new_task_name: TaskName) -> None:
        """
        タスク名を更新
        設計書の更新時の振る舞いに対応
        """
        if not new_task_name:
            raise TaskValidationException("新しいタスク名は必須です")

        # TaskNameの更新
        self._task_name = new_task_name

        # UpdatedAtの更新
        self._updated_at = UpdatedAt()

        # 不変条件の再検証
        self._validate_invariants(
            self._task_id, self._task_name, self._status,
            self._created_at, self._updated_at
        )

    def create_domain_event(self, user_id: str = "system") -> TaskCreatedEvent:
        """TaskCreatedEventを生成"""
        return TaskCreatedEvent(
            task_id=str(self._task_id),
            task_name=str(self._task_name),
            user_id=user_id,
            created_at=self._created_at.value
        )

    # プロパティ（読み取り専用）
    @property
    def task_id(self) -> TaskId:
        return self._task_id

    @property
    def task_name(self) -> TaskName:
        return self._task_name

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def created_at(self) -> CreatedAt:
        return self._created_at

    @property
    def updated_at(self) -> UpdatedAt:
        return self._updated_at

    # 同一性判定（設計書の等価性仕様）
    def __eq__(self, other: Any) -> bool:
        """
        同一性判定: taskId による比較
        BIV-003: 同一のtaskIdを持つTaskは同一のエンティティである
        """
        if not isinstance(other, Task):
            return False
        return self._task_id == other._task_id

    def __hash__(self) -> int:
        """ハッシュ値: taskId のハッシュ値"""
        return hash(self._task_id)

    def __repr__(self) -> str:
        return (
            f"Task(id='{self._task_id}', "
            f"name='{self._task_name}', "
            f"status='{self._status}', "
            f"created_at='{self._created_at}', "
            f"updated_at='{self._updated_at}')"
        )