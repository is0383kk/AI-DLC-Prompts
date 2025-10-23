"""
TaskRepositoryインターフェース
設計書のリポジトリ契約に基づく実装
"""
from abc import ABC, abstractmethod
from typing import Optional, List


class TaskRepository(ABC):
    """タスクリポジトリのインターフェース"""

    @abstractmethod
    async def save(self, task: 'Task') -> 'Task':
        """
        タスクの保存（作成・更新）
        事前条件: taskは有効なTaskエンティティである
        事後条件: taskがデータストアに永続化される
        """
        pass

    @abstractmethod
    async def find_by_id(self, task_id: 'TaskId') -> Optional['Task']:
        """
        IDによるタスク検索
        事前条件: task_idは有効なTaskIdである
        事後条件: 対象のTaskが存在する場合、完全なTaskエンティティを返す
        """
        pass

    @abstractmethod
    async def exists(self, task_id: 'TaskId') -> bool:
        """
        タスクの存在確認
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List['Task']:
        """
        ユーザーIDによるタスク検索（将来拡張用）
        """
        pass