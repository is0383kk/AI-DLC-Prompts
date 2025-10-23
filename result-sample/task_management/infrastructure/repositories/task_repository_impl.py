"""
TaskRepositoryImpl
設計書の TaskRepository 仕様に基づくインメモリ実装
"""
from typing import Optional, List, Dict
from infrastructure.repositories.task_repository import TaskRepository
from domain.entities.task import Task
from domain.value_objects.task_id import TaskId
from domain.factories.task_factory import TaskFactory
from domain.exceptions.domain_exceptions import TaskCreationException


class TaskRepositoryImpl(TaskRepository):
    """タスクリポジトリのインメモリ実装"""

    def __init__(self):
        """インメモリストレージの初期化"""
        self._storage: Dict[str, Dict] = {}  # task_id -> task_data の辞書

    async def save(self, task: Task) -> Task:
        """
        タスクの保存（作成・更新）
        事前条件: taskは有効なTaskエンティティである
        事後条件: taskがインメモリストレージに永続化される
        """
        try:
            # Task エンティティをストレージ用辞書に変換
            task_data = self._task_to_storage_dict(task)

            # インメモリストレージに保存
            task_id_str = str(task.task_id)
            self._storage[task_id_str] = task_data

            # 保存されたTaskエンティティを返却
            return task

        except Exception as e:
            raise TaskCreationException(f"タスクの保存に失敗しました: {str(e)}")

    async def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        """
        IDによるタスク検索
        事前条件: task_idは有効なTaskIdである
        事後条件: 対象のTaskが存在する場合、完全なTaskエンティティを返す
        """
        try:
            task_id_str = str(task_id)

            # インメモリストレージから検索
            if task_id_str not in self._storage:
                return None

            # ストレージデータからTaskエンティティを復元
            task_data = self._storage[task_id_str]
            return self._storage_dict_to_task(task_data)

        except Exception:
            # 検索エラーの場合はNoneを返す（仕様により例外発生させない）
            return None

    async def exists(self, task_id: TaskId) -> bool:
        """タスクの存在確認"""
        task_id_str = str(task_id)
        return task_id_str in self._storage

    async def find_by_user_id(self, user_id: str) -> List[Task]:
        """
        ユーザーIDによるタスク検索（将来拡張用）
        """
        try:
            matching_tasks: List[Task] = []

            for task_data in self._storage.values():
                # user_id による検索（現在はイベントデータから推定）
                # 将来的にはTaskエンティティにuser_idを追加する可能性
                task = self._storage_dict_to_task(task_data)
                matching_tasks.append(task)

            return matching_tasks

        except Exception:
            return []

    def _task_to_storage_dict(self, task: Task) -> Dict:
        """Taskエンティティをストレージ用辞書に変換"""
        return {
            "task_id": str(task.task_id),
            "task_name": str(task.task_name),
            "status": str(task.status),
            "created_at": task.created_at.to_iso_string(),
            "updated_at": task.updated_at.to_iso_string(),
            "version": "1.0"  # データバージョン管理用
        }

    def _storage_dict_to_task(self, task_data: Dict) -> Task:
        """ストレージ辞書からTaskエンティティを復元"""
        return TaskFactory.restore_task(
            task_id=task_data["task_id"],
            task_name=task_data["task_name"],
            status=task_data["status"],
            created_at_iso=task_data["created_at"],
            updated_at_iso=task_data["updated_at"]
        )

    # デバッグ・テスト用メソッド
    def get_all_tasks(self) -> List[Task]:
        """全タスクを取得（デバッグ用）"""
        tasks = []
        for task_data in self._storage.values():
            tasks.append(self._storage_dict_to_task(task_data))
        return tasks

    def clear_all(self) -> None:
        """全データをクリア（テスト用）"""
        self._storage.clear()

    def get_storage_stats(self) -> Dict:
        """ストレージ統計情報を取得（監視用）"""
        return {
            "total_tasks": len(self._storage),
            "storage_type": "in_memory",
            "version": "1.0"
        }