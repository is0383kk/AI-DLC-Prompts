"""
TaskCreationApplicationService
設計書の TaskCreationApplicationService 仕様に基づく実装
タスク作成ユースケースの実行統括
"""
import logging
from typing import Union
from application.commands.create_task_command import CreateTaskCommand
from application.responses.create_task_response import CreateTaskResponse
from application.responses.create_task_error_response import CreateTaskErrorResponse
from domain.services.task_creation_domain_service import TaskCreationDomainService
from domain.exceptions.domain_exceptions import (
    TaskValidationException,
    TaskSecurityException,
    TaskBusinessRuleViolationException,
    TaskCreationException
)
from infrastructure.repositories.task_repository import TaskRepository
from infrastructure.events.event_publisher import EventPublisher


class TaskCreationApplicationService:
    """タスク作成ユースケースの実行統括"""

    def __init__(
        self,
        task_repository: TaskRepository,
        event_publisher: EventPublisher,
        logger: logging.Logger = None
    ):
        """
        TaskCreationApplicationService を作成

        依存関係:
        - TaskRepository（永続化）
        - EventPublisher（イベント発行）
        - Logger（ログ出力）
        """
        self.task_repository = task_repository
        self.event_publisher = event_publisher
        self.logger = logger or logging.getLogger(__name__)
        self.domain_service = TaskCreationDomainService()

    async def create_task(
        self,
        command: CreateTaskCommand
    ) -> Union[CreateTaskResponse, CreateTaskErrorResponse]:
        """
        新しいタスクを作成する（US-001, US-002対応）

        処理フロー:
        1. [事前処理] コマンド検証とログ出力
        2. [認証] ユーザー認証状態の確認（スキップ：設定により不要）
        3. [認可] タスク作成権限の確認（スキップ：設定により不要）
        4. [トランザクション開始]
        5. [ドメイン処理] TaskCreationDomainService.createNewTask()
        6. [永続化] TaskRepository.save()
        7. [イベント発行] EventPublisher.publish(TaskCreatedEvent)
        8. [トランザクション確定]
        9. [事後処理] レスポンス生成とログ出力

        事前条件:
        - 有効なCreateTaskCommandが提供される

        事後条件:
        - タスクが永続化される
        - TaskCreatedEventが発行される
        - 成功/失敗レスポンスが返される
        """
        # 1. [事前処理] コマンド検証とログ出力
        self.logger.info(
            f"Task creation started for user: {command.user_id}, "
            f"request_id: {command.request_id}"
        )

        try:
            # 2. [認証] ユーザー認証状態の確認（設定により不要のためスキップ）
            # 3. [認可] タスク作成権限の確認（設定により不要のためスキップ）

            # 4. [トランザクション開始] （簡易実装：インメモリのため実質的な制御なし）

            # 5. [ドメイン処理] TaskCreationDomainService.createNewTask()
            creation_context = command.to_creation_context()
            task_creation_result = self.domain_service.create_new_task(
                task_name=command.task_name,
                creation_context=creation_context
            )

            # 6. [永続化] TaskRepository.save()
            saved_task = await self.task_repository.save(task_creation_result.get_task())

            # 7. [イベント発行] EventPublisher.publish(TaskCreatedEvent)
            await self.event_publisher.publish(task_creation_result.get_event())

            # 8. [トランザクション確定] （簡易実装：インメモリのため実質的な制御なし）

            # 9. [事後処理] レスポンス生成とログ出力
            response = CreateTaskResponse.from_task_creation_result(
                task_creation_result, command.request_id
            )

            self.logger.info(
                f"Task created successfully: {saved_task.task_id}, "
                f"request_id: {command.request_id}"
            )

            return response

        except TaskValidationException as e:
            # バリデーションエラー（BR-003対応）
            self.logger.warning(
                f"Task creation validation failed: {e.message}, "
                f"request_id: {command.request_id}"
            )
            return CreateTaskErrorResponse.from_validation_exception(e, command.request_id)

        except TaskBusinessRuleViolationException as e:
            # ビジネスルール違反（BR-003対応）
            self.logger.warning(
                f"Task creation business rule violation: {e.message}, "
                f"request_id: {command.request_id}"
            )
            return CreateTaskErrorResponse.from_business_rule_violation(e, command.request_id)

        except TaskSecurityException as e:
            # セキュリティエラー
            self.logger.error(
                f"Task creation security error: {e.message}, "
                f"user_id: {command.user_id}, "
                f"request_id: {command.request_id}"
            )
            return CreateTaskErrorResponse.from_security_exception(e, command.request_id)

        except TaskCreationException as e:
            # タスク作成エラー
            self.logger.error(
                f"Task creation failed: {e.message}, "
                f"request_id: {command.request_id}"
            )
            return CreateTaskErrorResponse.from_infrastructure_error(
                "タスクの作成に失敗しました", command.request_id
            )

        except Exception as e:
            # その他の予期しないエラー
            self.logger.error(
                f"Unexpected error during task creation: {str(e)}, "
                f"request_id: {command.request_id}",
                exc_info=True
            )
            return CreateTaskErrorResponse.from_unknown_error(command.request_id)

    def get_creation_metrics(self) -> dict:
        """作成メトリクスを取得（監視・分析用）"""
        # 実装例: 実際の実装では外部メトリクス収集システムと連携
        return {
            "service_name": "TaskCreationApplicationService",
            "version": "1.0.0",
            "status": "active"
        }