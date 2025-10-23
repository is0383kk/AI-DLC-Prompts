"""
LoggerImpl
設計書の Logger 仕様に基づく実装
統一されたログ出力機能の提供
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """ログレベル定義"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class LogContext:
    """ログコンテキスト情報"""

    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        operation: Optional[str] = None,
        duration: Optional[float] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.task_id = task_id
        self.operation = operation
        self.duration = duration
        self.additional_data = additional_data or {}


class StructuredLogData:
    """構造化ログデータ"""

    def __init__(
        self,
        message: str,
        level: LogLevel,
        context: Optional[LogContext] = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.level = level
        self.context = context or LogContext()
        self.extra_fields = extra_fields or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """構造化ログを辞書形式に変換"""
        log_dict = {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
        }

        # コンテキスト情報の追加
        if self.context:
            if self.context.request_id:
                log_dict["request_id"] = self.context.request_id
            if self.context.user_id:
                log_dict["user_id"] = self._mask_sensitive_data(self.context.user_id, "user_id")
            if self.context.task_id:
                log_dict["task_id"] = self.context.task_id
            if self.context.operation:
                log_dict["operation"] = self.context.operation
            if self.context.duration is not None:
                log_dict["duration"] = self.context.duration
            if self.context.additional_data:
                log_dict["additional_data"] = self._mask_sensitive_dict(self.context.additional_data)

        # 追加フィールドの追加
        if self.extra_fields:
            log_dict.update(self._mask_sensitive_dict(self.extra_fields))

        return log_dict

    def _mask_sensitive_data(self, value: str, field_name: str) -> str:
        """個人情報の適切なマスキング"""
        sensitive_fields = ["user_id", "email", "phone", "password", "token"]

        if field_name.lower() in sensitive_fields:
            if len(value) <= 4:
                return "***"
            else:
                return value[:2] + "***" + value[-2:]
        return value

    def _mask_sensitive_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """辞書内の機密情報をマスキング"""
        masked_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self._mask_sensitive_data(value, key)
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_dict(value)
            else:
                masked_data[key] = value
        return masked_data


class LoggerImpl:
    """統一ログ出力機能の実装"""

    def __init__(self, name: str = "TaskManagement", log_level: LogLevel = LogLevel.INFO):
        """LoggerImpl を初期化"""
        self.name = name
        self.log_level = log_level
        self._python_logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Python標準ログの設定"""
        if not self._python_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._python_logger.addHandler(handler)
            self._python_logger.setLevel(getattr(logging, self.log_level.value))

    def info(self, message: str, context: Optional[LogContext] = None) -> None:
        """INFOレベルログ出力"""
        if self._should_log(LogLevel.INFO):
            structured_data = StructuredLogData(message, LogLevel.INFO, context)
            self._output_structured_log(structured_data)

    def warn(self, message: str, context: Optional[LogContext] = None) -> None:
        """WARNINGレベルログ出力"""
        if self._should_log(LogLevel.WARN):
            structured_data = StructuredLogData(message, LogLevel.WARN, context)
            self._output_structured_log(structured_data)

    def error(self, message: str, error: Optional[Exception] = None, context: Optional[LogContext] = None) -> None:
        """ERRORレベルログ出力"""
        if self._should_log(LogLevel.ERROR):
            extra_fields = {}
            if error:
                extra_fields["error_type"] = type(error).__name__
                extra_fields["error_message"] = str(error)

            structured_data = StructuredLogData(message, LogLevel.ERROR, context, extra_fields)
            self._output_structured_log(structured_data)

    def debug(self, message: str, context: Optional[LogContext] = None) -> None:
        """DEBUGレベルログ出力"""
        if self._should_log(LogLevel.DEBUG):
            structured_data = StructuredLogData(message, LogLevel.DEBUG, context)
            self._output_structured_log(structured_data)

    def log_structured(self, level: LogLevel, data: StructuredLogData) -> None:
        """構造化ログ出力"""
        if self._should_log(level):
            self._output_structured_log(data)

    def log_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """メトリクス出力"""
        metric_data = {
            "metric_name": name,
            "metric_value": value,
            "metric_tags": tags or {},
            "metric_timestamp": datetime.now().isoformat()
        }

        context = LogContext(
            operation="metric",
            additional_data=metric_data
        )

        self.info(f"Metric: {name} = {value}", context)

    def _should_log(self, level: LogLevel) -> bool:
        """ログレベルチェック"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3
        }
        return level_order[level] >= level_order[self.log_level]

    def _output_structured_log(self, data: StructuredLogData) -> None:
        """構造化ログの実際の出力処理"""
        # JSON形式での構造化ログ出力
        log_json = json.dumps(data.to_dict(), ensure_ascii=False, separators=(',', ':'))

        # Python標準ログへの出力
        python_level = getattr(logging, data.level.value)
        self._python_logger.log(python_level, log_json)


class TaskManagementLogger:
    """タスク管理アプリケーション専用ログ機能"""

    def __init__(self):
        self.logger = LoggerImpl("TaskManagement")

    def log_task_creation_start(self, request_id: str, user_id: str, task_name: str) -> None:
        """タスク作成開始ログ"""
        context = LogContext(
            request_id=request_id,
            user_id=user_id,
            operation="task_creation_start",
            additional_data={"task_name_length": len(task_name)}
        )
        self.logger.info("Task creation started", context)

    def log_task_creation_success(self, request_id: str, task_id: str, duration: float) -> None:
        """タスク作成成功ログ"""
        context = LogContext(
            request_id=request_id,
            task_id=task_id,
            operation="task_creation_success",
            duration=duration
        )
        self.logger.info("Task creation completed successfully", context)

    def log_task_creation_failure(self, request_id: str, error: Exception, duration: float) -> None:
        """タスク作成失敗ログ"""
        context = LogContext(
            request_id=request_id,
            operation="task_creation_failure",
            duration=duration
        )
        self.logger.error("Task creation failed", error, context)

    def log_validation_error(self, request_id: str, violations: list) -> None:
        """バリデーションエラーログ"""
        context = LogContext(
            request_id=request_id,
            operation="validation_error",
            additional_data={"violations_count": len(violations)}
        )
        self.logger.warn("Validation errors occurred", context)

    def log_security_event(self, request_id: str, threat_type: str, user_id: str) -> None:
        """セキュリティイベントログ"""
        context = LogContext(
            request_id=request_id,
            user_id=user_id,
            operation="security_event",
            additional_data={"threat_type": threat_type}
        )
        self.logger.error("Security event detected", context=context)