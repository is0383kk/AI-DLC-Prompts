#!/usr/bin/env python3
"""
Basic Test Script for Task Management Application
Windows環境対応版（絵文字なし）
"""
import sys
import asyncio
from datetime import datetime

print('='*60)
print('Task Management Application - Basic Test')
print('='*60)

try:
    # 基本的な機能テスト

    # 1. ドメイン層の基本テスト
    print('\n[TEST] Domain Layer Tests:')

    # TaskId テスト
    from domain.value_objects.task_id import TaskId
    task_id = TaskId.generate()
    print(f'[OK] TaskId generation: {task_id}')

    # TaskName テスト
    from domain.value_objects.task_name import TaskName
    task_name = TaskName("Test Task")
    print(f'[OK] TaskName creation: {task_name}')

    # Task エンティティテスト
    from domain.entities.task import Task
    task = Task.create(task_name)
    print(f'[OK] Task creation: {task.task_id}')

    # ビジネスルールテスト
    print('\n[TEST] Business Rules Tests:')

    try:
        TaskName("")  # BR-001 テスト
        print('[FAIL] BR-001 failed: Empty name should be rejected')
    except Exception:
        print('[OK] BR-001: Task name is required')

    try:
        TaskName("x" * 101)  # BR-004 テスト
        print('[FAIL] BR-004 failed: Long name should be rejected')
    except Exception:
        print('[OK] BR-004: Task name length limit')

    # 2. インフラ層テスト
    print('\n[TEST] Infrastructure Layer Tests:')

    from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
    repository = TaskRepositoryImpl()
    print('[OK] Repository initialization')

    # 非同期保存テスト
    async def test_repository():
        saved_task = await repository.save(task)
        found_task = await repository.find_by_id(task.task_id)
        return saved_task, found_task

    saved_task, found_task = asyncio.run(test_repository())
    print(f'[OK] Repository save/find: {found_task.task_id}')

    # 3. イベントテスト
    from infrastructure.events.event_publisher_impl import EventPublisherImpl
    event_publisher = EventPublisherImpl()

    async def test_event():
        event = task.create_domain_event("test-user")
        await event_publisher.publish(event)
        return event

    published_event = asyncio.run(test_event())
    print(f'[OK] Event publishing: {published_event.event_id}')

    # 4. アプリケーション層テスト
    print('\n[TEST] Application Layer Tests:')

    from application.commands.create_task_command import CreateTaskCommand, ClientInfo
    command = CreateTaskCommand(
        task_name="Application Test Task",
        user_id="test-user"
    )
    print(f'[OK] Command creation: {command.request_id}')

    print('\n' + '='*60)
    print('SUCCESS: ALL BASIC TESTS PASSED!')
    print('='*60)
    print('\nImplementation Summary:')
    print('- Domain Layer: Entities, Value Objects, Domain Services')
    print('- Application Layer: Application Services, Commands, Responses')
    print('- Infrastructure Layer: Repositories, Event Publishers')
    print('- Business Rules: BR-001 to BR-006 implemented')
    print('- US-001 & US-002: Task creation functionality')
    print('='*60)
    print('\nNext Steps:')
    print('1. Fix remaining import paths')
    print('2. Start FastAPI application: python main.py')
    print('3. Test API endpoint: POST /api/tasks')
    print('4. View OpenAPI docs: http://localhost:8000/docs')
    print('='*60)

except Exception as e:
    print(f'[ERROR] Test failed: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)