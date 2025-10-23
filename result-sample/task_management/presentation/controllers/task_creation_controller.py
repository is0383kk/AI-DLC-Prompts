"""
TaskCreationController
設計書の TaskCreationController 仕様に基づく実装
POST /api/tasks エンドポイントの提供
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, Depends
from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Union

from presentation.dtos.create_task_request_dto import CreateTaskRequestDTO
from presentation.dtos.task_response_dto import TaskResponseDTO
from presentation.dtos.error_response_dto import ErrorResponseDTO, ErrorDetailDTO
from application.services.task_creation_application_service import TaskCreationApplicationService
from application.commands.create_task_command import CreateTaskCommand, ClientInfo
from application.responses.create_task_response import CreateTaskResponse
from application.responses.create_task_error_response import CreateTaskErrorResponse
from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from infrastructure.events.event_publisher_impl import EventPublisherImpl
from infrastructure.logging.logger_impl import TaskManagementLogger


class TaskCreationController:
    """タスク作成API コントローラー"""

    def __init__(self):
        """依存関係の初期化"""
        self.task_repository = TaskRepositoryImpl()
        self.event_publisher = EventPublisherImpl()
        self.logger = TaskManagementLogger()
        self.application_service = TaskCreationApplicationService(
            task_repository=self.task_repository,
            event_publisher=self.event_publisher,
            logger=self.logger.logger._python_logger
        )

    def create_router(self) -> APIRouter:
        """FastAPI ルーターを作成"""
        router = APIRouter(prefix="/api", tags=["tasks"])

        @router.post(
            "/tasks",
            response_model=TaskResponseDTO,
            status_code=HTTPStatus.CREATED,
            summary="新しいタスクを作成",
            description="タスク作成機能（US-001, US-002対応）",
            responses={
                201: {
                    "description": "タスクが正常に作成されました",
                    "model": TaskResponseDTO
                },
                400: {
                    "description": "バリデーションエラー",
                    "model": ErrorResponseDTO
                },
                422: {
                    "description": "ビジネスルール違反",
                    "model": ErrorResponseDTO
                },
                500: {
                    "description": "サーバーエラー",
                    "model": ErrorResponseDTO
                }
            }
        )
        async def create_task(
            request_dto: CreateTaskRequestDTO,
            request: Request
        ) -> Union[JSONResponse, TaskResponseDTO]:
            """
            POST /api/tasks エンドポイント

            タスク作成処理:
            1. HTTP リクエストからDTOへの変換
            2. DTOからコマンドオブジェクトへの変換
            3. アプリケーションサービスの呼び出し
            4. レスポンスオブジェクトからDTOへの変換
            5. HTTP レスポンスの返却
            """
            # リクエストID生成
            request_id = str(uuid.uuid4())

            try:
                # クライアント情報の取得
                client_info = ClientInfo(
                    user_agent=request.headers.get("user-agent", "unknown"),
                    ip_address=request.client.host if request.client else "127.0.0.1",
                    platform="web"
                )

                # DTOからコマンドオブジェクトへの変換
                command = CreateTaskCommand(
                    task_name=request_dto.task_name,
                    user_id=request_dto.user_id,
                    request_id=request_id,
                    timestamp=datetime.now(),
                    client_info=client_info
                )

                # アプリケーションサービスの呼び出し
                result = await self.application_service.create_task(command)

                # 成功レスポンスの処理
                if isinstance(result, CreateTaskResponse):
                    response_dto = TaskResponseDTO(
                        task_id=result.task_id,
                        task_name=result.task_name,
                        status=result.status,
                        created_at=result.created_at,
                        message=result.message
                    )
                    return JSONResponse(
                        status_code=HTTPStatus.CREATED,
                        content=response_dto.dict()
                    )

                # エラーレスポンスの処理
                elif isinstance(result, CreateTaskErrorResponse):
                    return await self._handle_error_response(result)

                else:
                    # 予期しない結果タイプ
                    return await self._handle_unknown_error(request_id)

            except Exception as e:
                # 予期しない例外の処理
                self.logger.logger.error(f"Unexpected error in controller: {str(e)}")
                return await self._handle_unknown_error(request_id)

        return router

    async def _handle_error_response(self, error_response: CreateTaskErrorResponse) -> JSONResponse:
        """エラーレスポンスの処理"""
        # エラー詳細の変換
        error_details = []
        for detail in error_response.details:
            error_details.append(ErrorDetailDTO(
                field=detail.field,
                code=detail.code,
                message=detail.message,
                value=detail.value
            ))

        # ErrorResponseDTO の作成
        error_dto = ErrorResponseDTO(
            error_code=error_response.error_code,
            error_message=error_response.error_message,
            details=error_details,
            timestamp=error_response.timestamp,
            request_id=error_response.request_id
        )

        # HTTP ステータスコードの決定
        status_code = self._get_http_status_code(error_response.error_code)

        return JSONResponse(
            status_code=status_code,
            content=error_dto.dict()
        )

    async def _handle_unknown_error(self, request_id: str) -> JSONResponse:
        """不明なエラーの処理"""
        error_dto = ErrorResponseDTO(
            error_code="UNKNOWN_ERROR",
            error_message="予期しないエラーが発生しました",
            details=[],
            timestamp=datetime.now(),
            request_id=request_id
        )

        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=error_dto.dict()
        )

    def _get_http_status_code(self, error_code: str) -> int:
        """エラーコードからHTTPステータスコードを決定"""
        status_mapping = {
            "VALIDATION_ERROR": HTTPStatus.BAD_REQUEST,
            "SECURITY_ERROR": HTTPStatus.FORBIDDEN,
            "BUSINESS_RULE_VIOLATION": HTTPStatus.UNPROCESSABLE_ENTITY,
            "INFRASTRUCTURE_ERROR": HTTPStatus.INTERNAL_SERVER_ERROR,
            "UNKNOWN_ERROR": HTTPStatus.INTERNAL_SERVER_ERROR
        }

        return status_mapping.get(error_code, HTTPStatus.INTERNAL_SERVER_ERROR)


# ルーター作成用のファクトリ関数
def create_task_router() -> APIRouter:
    """タスク作成ルーターを作成"""
    controller = TaskCreationController()
    return controller.create_router()