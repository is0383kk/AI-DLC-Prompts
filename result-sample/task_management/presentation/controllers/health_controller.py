"""
ヘルスチェックコントローラー
詳細なヘルスチェック・依存関係チェック・システムリソース状態チェック
"""
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from infrastructure.events.event_publisher_impl import EventPublisherImpl
from infrastructure.logging.logger_impl import TaskManagementLogger


class HealthController:
    """詳細ヘルスチェック機能を提供するコントローラー"""

    def __init__(self):
        """依存関係の初期化"""
        self.task_repository = TaskRepositoryImpl()
        self.event_publisher = EventPublisherImpl()
        self.logger = TaskManagementLogger()
        self.start_time = time.time()

    def create_router(self) -> APIRouter:
        """ヘルスチェック用ルーターを作成"""
        router = APIRouter(prefix="/health", tags=["health"])

        @router.get(
            "/",
            summary="基本ヘルスチェック",
            description="アプリケーションの基本的な稼働状態を確認",
            response_description="基本的なヘルス情報"
        )
        async def basic_health():
            """基本ヘルスチェック（既存の/healthと同等）"""
            return {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "Task Management API - Unit1",
                "version": "1.0.0",
                "uptime_seconds": int(time.time() - self.start_time)
            }

        @router.get(
            "/detailed",
            summary="詳細ヘルスチェック",
            description="アプリケーション・依存関係・システムリソースの詳細状態を確認",
            response_description="詳細なヘルス情報"
        )
        async def detailed_health():
            """詳細ヘルスチェック"""
            try:
                health_data = await self._get_detailed_health_data()

                # 全体的な健康状態の判定
                overall_status = self._determine_overall_status(health_data)
                http_status = status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

                return JSONResponse(
                    status_code=http_status,
                    content={
                        "status": overall_status,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "checks": health_data
                    }
                )

            except Exception as e:
                self.logger.logger.error(f"Health check failed: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "unhealthy",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": "ヘルスチェック実行中にエラーが発生しました",
                        "details": str(e)
                    }
                )

        @router.get(
            "/readiness",
            summary="稼働準備状態チェック",
            description="アプリケーションがリクエストを受け付ける準備ができているかを確認",
            response_description="稼働準備状態"
        )
        async def readiness_check():
            """稼働準備状態チェック（Kubernetes readiness probe用）"""
            try:
                # アプリケーション層の準備状態確認
                app_ready = await self._check_application_readiness()

                if app_ready:
                    return {
                        "status": "ready",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "message": "アプリケーションはリクエストを受け付ける準備ができています"
                    }
                else:
                    return JSONResponse(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content={
                            "status": "not_ready",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "message": "アプリケーションは準備中です"
                        }
                    )

            except Exception as e:
                self.logger.logger.error(f"Readiness check failed: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "not_ready",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": str(e)
                    }
                )

        @router.get(
            "/liveness",
            summary="生存状態チェック",
            description="アプリケーションが生きているかを確認",
            response_description="生存状態"
        )
        async def liveness_check():
            """生存状態チェック（Kubernetes liveness probe用）"""
            try:
                # 基本的な生存確認（この関数が実行できること自体が生存の証拠）
                return {
                    "status": "alive",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "uptime_seconds": int(time.time() - self.start_time),
                    "message": "アプリケーションは正常に動作しています"
                }

            except Exception as e:
                self.logger.logger.error(f"Liveness check failed: {str(e)}")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "status": "dead",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error": str(e)
                    }
                )

        return router

    async def _get_detailed_health_data(self) -> Dict[str, Dict[str, Any]]:
        """詳細ヘルスチェックデータを取得"""
        return {
            "application": await self._check_application_health(),
            "dependencies": await self._check_dependencies_health(),
            "system_resources": await self._check_system_resources(),
            "business_metrics": await self._check_business_metrics()
        }

    async def _check_application_health(self) -> Dict[str, Any]:
        """アプリケーション状態チェック"""
        try:
            return {
                "status": "healthy",
                "layers": {
                    "domain_layer": "active",
                    "application_layer": "active",
                    "infrastructure_layer": "active",
                    "presentation_layer": "active"
                },
                "uptime_seconds": int(time.time() - self.start_time),
                "version": "1.0.0",
                "environment": "development"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def _check_dependencies_health(self) -> Dict[str, Any]:
        """依存サービス状態チェック"""
        try:
            # タスクリポジトリの健康状態確認
            repository_stats = self.task_repository.get_storage_stats()

            # イベントパブリッシャーの健康状態確認
            publisher_stats = self.event_publisher.get_publisher_stats()

            return {
                "status": "healthy",
                "components": {
                    "task_repository": {
                        "status": "healthy",
                        "type": repository_stats.get("storage_type", "unknown"),
                        "total_tasks": repository_stats.get("total_tasks", 0)
                    },
                    "event_publisher": {
                        "status": "healthy",
                        "published_events": publisher_stats.get("total_published", 0),
                        "failed_events": publisher_stats.get("total_failed", 0)
                    },
                    "logger": {
                        "status": "healthy",
                        "type": "TaskManagementLogger"
                    }
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def _check_system_resources(self) -> Dict[str, Any]:
        """システムリソース状態チェック"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # メモリ使用率
            memory = psutil.virtual_memory()

            # ディスク使用率
            disk = psutil.disk_usage('/')

            return {
                "status": "healthy",
                "cpu": {
                    "usage_percent": cpu_percent,
                    "status": "normal" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "usage_percent": memory.percent,
                    "available_gb": round(memory.available / (1024**3), 2),
                    "status": "normal" if memory.percent < 80 else "high"
                },
                "disk": {
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "status": "normal" if (disk.used / disk.total) < 0.8 else "high"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def _check_business_metrics(self) -> Dict[str, Any]:
        """ビジネスメトリクス確認"""
        try:
            # タスク作成関連のメトリクス
            all_tasks = self.task_repository.get_all_tasks()
            task_count = len(all_tasks)

            # イベント発行統計
            publisher_stats = self.event_publisher.get_publisher_stats()

            return {
                "status": "healthy",
                "metrics": {
                    "total_tasks_created": task_count,
                    "total_events_published": publisher_stats.get("total_published", 0),
                    "uptime_seconds": int(time.time() - self.start_time),
                    "average_response_time": "< 100ms"  # 実装では実際の測定値を使用
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def _check_application_readiness(self) -> bool:
        """アプリケーション稼働準備状態確認"""
        try:
            # 基本的な依存関係の確認
            repository_stats = self.task_repository.get_storage_stats()
            publisher_stats = self.event_publisher.get_publisher_stats()

            # リポジトリとイベントパブリッシャーが正常に初期化されていることを確認
            return (
                repository_stats is not None and
                publisher_stats is not None
            )
        except Exception:
            return False

    def _determine_overall_status(self, health_data: Dict[str, Dict[str, Any]]) -> str:
        """全体的な健康状態を判定"""
        for component_name, component_data in health_data.items():
            if component_data.get("status") != "healthy":
                return "unhealthy"
        return "healthy"


# ルーター作成用のファクトリ関数
def create_health_router() -> APIRouter:
    """ヘルスチェックルーターを作成"""
    controller = HealthController()
    return controller.create_router()