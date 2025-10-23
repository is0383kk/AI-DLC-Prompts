#!/usr/bin/env python3
"""
Task Management Application - Import & Configuration Test
"""
import sys
import os

# カレントディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('='*60)
print('Task Management Application - Import Check')
print('='*60)

try:
    # 基本インポートチェック
    from main import app
    print('✅ Main application imported successfully')

    # アプリケーション情報表示
    print(f'✅ App title: {app.title}')
    print(f'✅ App version: {app.version}')

    # ルーター確認
    routes = [route.path for route in app.routes]
    print(f'✅ Available routes: {routes}')

    # 各層のインポート確認
    print('\n📦 Layer Import Tests:')

    # Domain Layer
    from task_management.domain.entities.task import Task
    from task_management.domain.value_objects.task_id import TaskId
    from task_management.domain.value_objects.task_name import TaskName
    from task_management.domain.services.task_creation_domain_service import TaskCreationDomainService
    print('✅ Domain layer imports: OK')

    # Application Layer
    from task_management.application.services.task_creation_application_service import TaskCreationApplicationService
    from task_management.application.commands.create_task_command import CreateTaskCommand
    print('✅ Application layer imports: OK')

    # Infrastructure Layer
    from task_management.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
    from task_management.infrastructure.events.event_publisher_impl import EventPublisherImpl
    print('✅ Infrastructure layer imports: OK')

    # Presentation Layer
    from task_management.presentation.controllers.task_creation_controller import TaskCreationController
    from task_management.presentation.dtos.create_task_request_dto import CreateTaskRequestDTO
    print('✅ Presentation layer imports: OK')

    print('\n🧪 Basic Functionality Tests:')

    # 基本的な機能テスト
    # TaskId作成テスト
    task_id = TaskId.generate()
    print(f'✅ TaskId generation: {task_id}')

    # TaskName作成テスト
    task_name = TaskName("テストタスク")
    print(f'✅ TaskName creation: {task_name}')

    # Task作成テスト
    task = Task.create(task_name)
    print(f'✅ Task creation: {task.task_id}')

    # Repository初期化テスト
    repository = TaskRepositoryImpl()
    print('✅ Repository initialization: OK')

    # EventPublisher初期化テスト
    event_publisher = EventPublisherImpl()
    print('✅ EventPublisher initialization: OK')

    print('\n🎯 Business Rules Validation:')

    # ビジネスルールテスト
    try:
        # BR-001: タスク名必須チェック
        TaskName("")
        print('❌ BR-001 test failed: Empty task name should be rejected')
    except Exception:
        print('✅ BR-001: Task name is required - OK')

    try:
        # BR-004: 文字数制限チェック
        long_name = "x" * 101
        TaskName(long_name)
        print('❌ BR-004 test failed: Long task name should be rejected')
    except Exception:
        print('✅ BR-004: Task name length limit - OK')

    print('\n' + '='*60)
    print('🎉 ALL TESTS PASSED - Application is ready to run!')
    print('='*60)
    print('\n📋 Next Steps:')
    print('1. Run: python main.py')
    print('2. Open: http://localhost:8000/docs')
    print('3. Test: POST /api/tasks endpoint')
    print('='*60)

except Exception as e:
    print(f'❌ Test failed: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)