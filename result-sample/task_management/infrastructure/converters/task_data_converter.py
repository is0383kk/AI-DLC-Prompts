"""
TaskDataConverter
設計書の TaskDataConverter 仕様に基づく実装
ドメインエンティティと外部データ形式の変換
"""
from typing import Dict, Any
from datetime import datetime
from domain.entities.task import Task
from domain.factories.task_factory import TaskFactory
from domain.exceptions.domain_exceptions import TaskValidationException


class TaskDataInterface:
    """Unit2との統一データ形式定義"""

    def __init__(
        self,
        task_id: str,
        task_name: str,
        created_at: str,
        status: str,
        metadata: Dict[str, Any] = None
    ):
        """
        TaskDataInterface を作成
        制約条件:
        - task_id: 必須、UUID v4形式、36文字固定
        - task_name: 必須、1-100文字、HTMLエスケープ済み
        - created_at: 必須、ISO8601形式
        - status: 必須、事前定義値のみ
        """
        self.task_id = task_id
        self.task_name = task_name
        self.created_at = created_at
        self.status = status
        self.metadata = metadata or {
            "version": "1.0.0",
            "source": "unit1-task-creation",
            "last_modified": datetime.now().isoformat()
        }

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式への変換"""
        return {
            "taskId": self.task_id,
            "taskName": self.task_name,
            "createdAt": self.created_at,
            "status": self.status,
            "metadata": self.metadata
        }


class ValidationResult:
    """データ変換バリデーション結果"""

    def __init__(self, is_valid: bool, errors: list = None):
        self.is_valid = is_valid
        self.errors = errors or []


class TaskDataConverter:
    """ドメインエンティティと外部データ形式の変換"""

    CURRENT_VERSION = "1.0.0"
    COMPATIBLE_VERSIONS = ["1.0.0"]

    @staticmethod
    def to_task_data_interface(task: Task) -> TaskDataInterface:
        """
        ドメインエンティティから外部形式への変換

        変換ルール:
        1. TaskId → taskId: UUID文字列への変換
        2. TaskName → taskName: 値の取得とエスケープ確認
        3. CreatedAt → createdAt: ISO8601形式への変換
        4. TaskStatus → status: 文字列表現への変換
        5. メタデータの自動生成
        """
        try:
            if not task:
                raise TaskValidationException("Taskエンティティが指定されていません")

            # 1. TaskId → taskId: UUID文字列への変換
            task_id = str(task.task_id)

            # 2. TaskName → taskName: 値の取得とエスケープ確認
            task_name = str(task.task_name)

            # 3. CreatedAt → createdAt: ISO8601形式への変換
            created_at = task.created_at.to_iso_string()

            # 4. TaskStatus → status: 文字列表現への変換
            status = str(task.status)

            # 5. メタデータの自動生成
            metadata = {
                "version": TaskDataConverter.CURRENT_VERSION,
                "source": "unit1-task-creation",
                "last_modified": task.updated_at.to_iso_string(),
                "entity_type": "Task",
                "conversion_timestamp": datetime.now().isoformat()
            }

            return TaskDataInterface(
                task_id=task_id,
                task_name=task_name,
                created_at=created_at,
                status=status,
                metadata=metadata
            )

        except Exception as e:
            raise TaskValidationException(f"TaskDataInterface変換に失敗しました: {str(e)}")

    @staticmethod
    def from_task_data_interface(data: TaskDataInterface) -> Task:
        """
        外部形式からドメインエンティティへの変換（将来拡張用）
        """
        try:
            if not data:
                raise TaskValidationException("TaskDataInterfaceが指定されていません")

            # バリデーション
            validation_result = TaskDataConverter.validate_task_data_interface(data)
            if not validation_result.is_valid:
                raise TaskValidationException(f"データ形式が不正です: {validation_result.errors}")

            # TaskFactoryを使用してTaskエンティティを復元
            return TaskFactory.restore_task(
                task_id=data.task_id,
                task_name=data.task_name,
                status=data.status,
                created_at_iso=data.created_at,
                updated_at_iso=data.metadata.get("last_modified", data.created_at)
            )

        except Exception as e:
            raise TaskValidationException(f"Taskエンティティ復元に失敗しました: {str(e)}")

    @staticmethod
    def validate_task_data_interface(data: TaskDataInterface) -> ValidationResult:
        """TaskDataInterfaceのバリデーション"""
        errors = []

        try:
            # taskId バリデーション
            if not data.task_id:
                errors.append("taskId は必須です")
            else:
                import uuid
                try:
                    uuid.UUID(data.task_id)
                except ValueError:
                    errors.append("taskId はUUID形式である必要があります")

            # taskName バリデーション
            if not data.task_name:
                errors.append("taskName は必須です")
            elif len(data.task_name) > 100:
                errors.append("taskName は100文字以内である必要があります")

            # createdAt バリデーション
            if not data.created_at:
                errors.append("createdAt は必須です")
            else:
                try:
                    datetime.fromisoformat(data.created_at.replace('Z', '+00:00'))
                except ValueError:
                    errors.append("createdAt はISO8601形式である必要があります")

            # status バリデーション
            valid_statuses = ["未完了", "完了", "保留"]
            if not data.status:
                errors.append("status は必須です")
            elif data.status not in valid_statuses:
                errors.append(f"status は有効な値である必要があります: {valid_statuses}")

            # metadata バリデーション
            if data.metadata:
                version = data.metadata.get("version")
                if version and not TaskDataConverter.is_compatible_version(version):
                    errors.append(f"サポートされていないバージョンです: {version}")

            return ValidationResult(is_valid=len(errors) == 0, errors=errors)

        except Exception as e:
            errors.append(f"バリデーション処理でエラーが発生しました: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors)

    @staticmethod
    def is_compatible_version(version: str) -> bool:
        """バージョン互換性チェック"""
        return version in TaskDataConverter.COMPATIBLE_VERSIONS

    @staticmethod
    def convert_batch_to_task_data_interface(tasks: list) -> list:
        """複数Taskの一括変換"""
        try:
            converted_data = []
            for task in tasks:
                task_data_interface = TaskDataConverter.to_task_data_interface(task)
                converted_data.append(task_data_interface.to_dict())
            return converted_data

        except Exception as e:
            raise TaskValidationException(f"一括変換に失敗しました: {str(e)}")

    @staticmethod
    def get_conversion_stats() -> Dict[str, Any]:
        """変換統計情報を取得（監視用）"""
        return {
            "converter_version": TaskDataConverter.CURRENT_VERSION,
            "compatible_versions": TaskDataConverter.COMPATIBLE_VERSIONS,
            "supported_entity_types": ["Task"],
            "last_updated": datetime.now().isoformat()
        }