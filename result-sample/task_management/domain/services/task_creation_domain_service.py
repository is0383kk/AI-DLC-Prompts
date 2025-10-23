"""
TaskCreationDomainService
設計書の TaskCreationDomainService 仕様に基づく実装
タスク作成プロセス全体の調整とビジネスルールの実施
"""
from domain.factories.task_factory import TaskFactory, TaskCreationResult
from domain.services.task_validation_domain_service import (
    TaskValidationDomainService,
    TaskCreationContext
)
from domain.services.task_security_domain_service import (
    TaskSecurityDomainService,
    SanitizationPolicy
)
from domain.exceptions.domain_exceptions import (
    TaskValidationException,
    TaskSecurityException,
    TaskCreationException
)


class TaskCreationDomainService:
    """タスク作成プロセス全体の調整とビジネスルールの実施"""

    def __init__(self):
        self.validation_service = TaskValidationDomainService()
        self.security_service = TaskSecurityDomainService()

    def create_new_task(
        self,
        task_name: str,
        creation_context: TaskCreationContext
    ) -> TaskCreationResult:
        """
        新しいタスクを作成し、ビジネスルールを適用

        処理フロー:
        1. 入力パラメータの基本検証
        2. TaskValidationDomainServiceを使用したバリデーション
        3. TaskSecurityDomainServiceを使用したセキュリティ処理
        4. TaskFactoryを使用したエンティティ作成
        5. TaskCreatedEventの生成
        6. 結果の返却

        事前条件:
        - task_nameが提供されている
        - creation_contextが有効である

        事後条件:
        - 有効なTaskエンティティが作成される
        - TaskCreatedEventが生成される
        - 全てのビジネスルールが満たされる
        """
        try:
            # 1. 入力パラメータの基本検証
            self._validate_input_parameters(task_name, creation_context)

            # 2. TaskValidationDomainServiceを使用したバリデーション
            validation_result = self.validation_service.validate_task_creation(
                task_name, creation_context
            )

            if not validation_result.is_valid:
                error_messages = validation_result.get_error_messages()
                raise TaskValidationException(
                    "バリデーションに失敗しました",
                    violations=error_messages
                )

            # 3. TaskSecurityDomainServiceを使用したセキュリティ処理
            # 3-1. 入力サニタイゼーション
            sanitized_input = self.security_service.sanitize_task_input(
                task_name, SanitizationPolicy.STRICT
            )

            # 3-2. セキュリティ制約チェック
            security_result = self.security_service.check_security_constraints(
                sanitized_input.clean_input, creation_context
            )

            if not security_result.is_passed:
                critical_threats = security_result.get_critical_threats()
                if critical_threats:
                    threat_descriptions = [threat.description for threat in critical_threats]
                    raise TaskSecurityException(
                        "セキュリティ制約に違反しています",
                        threat_type="CRITICAL_THREAT_DETECTED"
                    )

            # 4. TaskFactoryを使用したエンティティ作成
            task_creation_result = TaskFactory.create_task_with_event(
                task_name=sanitized_input.clean_input,
                user_id=creation_context.user_id
            )

            # 5. 追加のビジネスルール適用
            self._apply_additional_business_rules(task_creation_result, creation_context)

            return task_creation_result

        except TaskValidationException:
            # バリデーション例外はそのまま再発生
            raise
        except TaskSecurityException:
            # セキュリティ例外はそのまま再発生
            raise
        except Exception as e:
            # その他の例外はTaskCreationExceptionでラップ
            raise TaskCreationException(f"タスク作成処理に失敗しました: {str(e)}")

    def _validate_input_parameters(
        self,
        task_name: str,
        creation_context: TaskCreationContext
    ) -> None:
        """入力パラメータの基本検証"""
        if task_name is None:
            raise TaskCreationException("task_name は必須です")

        if creation_context is None:
            raise TaskCreationException("creation_context は必須です")

        # TaskFactoryの事前条件確認を使用
        if not TaskFactory.validate_task_creation_prerequisites(
            task_name, creation_context.user_id
        ):
            raise TaskCreationException("タスク作成の事前条件を満たしていません")

    def _apply_additional_business_rules(
        self,
        task_creation_result: TaskCreationResult,
        creation_context: TaskCreationContext
    ) -> None:
        """追加のビジネスルール適用"""
        # BR-002: タスク保存時には確認メッセージを表示する必要がある
        # これはプレゼンテーション層で実装されるため、ここでは記録のみ

        # BR-006: 必須でない項目はデフォルト値またはNULLで初期化される
        # これはTaskFactoryで既に適用済み

        # 将来的な拡張ポイント:
        # - 作成数制限チェック
        # - 重複タスク名チェック
        # - ユーザー固有のビジネスルール適用
        pass

    def get_creation_summary(
        self,
        task_creation_result: TaskCreationResult
    ) -> dict:
        """作成結果のサマリー情報を取得（ログ・監査用）"""
        task = task_creation_result.get_task()
        event = task_creation_result.get_event()

        return {
            "task_id": str(task.task_id),
            "task_name": str(task.task_name),
            "status": str(task.status),
            "created_at": task.created_at.to_iso_string(),
            "event_id": event.event_id,
            "event_type": event.get_event_type(),
            "success": task_creation_result.is_success(),
            "created_by": event.user_id
        }