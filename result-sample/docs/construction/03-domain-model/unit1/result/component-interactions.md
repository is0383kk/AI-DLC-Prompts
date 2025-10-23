# コンポーネント相互作用設計書 - Unit1: タスク作成機能

## 作成情報

- **作成日**: 2025-10-22
- **設計対象**: タスク作成機能のコンポーネント間相互作用
- **分析フェーズ**: フェーズ6（統合とテスト設計）
- **参照元**: アプリケーションサービス設計書、インターフェース設計書

## 1. システム全体アーキテクチャ概要

### 1.1 レイヤー構成

```
┌─────────────────────────────────────┐
│     プレゼンテーション層              │
│  ┌─────────────────────────────────┐ │
│  │ TaskCreationController          │ │
│  │ CreateTaskRequestDTO            │ │
│  │ TaskResponseDTO                 │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    ↓ HTTP/JSON
┌─────────────────────────────────────┐
│       アプリケーション層              │
│  ┌─────────────────────────────────┐ │
│  │ TaskCreationApplicationService  │ │
│  │ CreateTaskCommand               │ │
│  │ CreateTaskResponse              │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    ↓ インメモリ呼び出し
┌─────────────────────────────────────┐
│         ドメイン層                   │
│  ┌─────────────────────────────────┐ │
│  │ TaskCreationDomainService       │ │
│  │ Task (エンティティ)              │ │
│  │ TaskFactory                     │ │
│  │ TaskCreatedEvent                │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
                    ↓ インターフェース経由
┌─────────────────────────────────────┐
│      インフラストラクチャ層           │
│  ┌─────────────────────────────────┐ │
│  │ TaskRepositoryImpl              │ │
│  │ EventPublisherImpl              │ │
│  │ SecurityServiceImpl             │ │
│  │ LoggerImpl                      │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 1.2 依存関係の方向

```
上位層 → 下位層への依存（具象への依存）
下位層 → 上位層への依存（インターフェースによる依存性逆転）

具体的な依存関係:
プレゼンテーション層 → アプリケーション層（直接依存）
アプリケーション層 → ドメイン層（直接依存）
アプリケーション層 → インフラ層（インターフェース経由）
ドメイン層 → インフラ層（インターフェース経由）
```

## 2. シーケンス図（マークダウン形式）

### 2.1 正常系：タスク作成成功フロー

```
【参加者】
- Client: クライアントアプリケーション
- Controller: TaskCreationController
- AppService: TaskCreationApplicationService
- DomainService: TaskCreationDomainService
- ValidationService: TaskValidationDomainService
- SecurityService: TaskSecurityDomainService
- Factory: TaskFactory
- Repository: TaskRepository
- EventPublisher: EventPublisher

【シーケンス】
Client -> Controller: POST /api/tasks
Note: CreateTaskRequestDTO {taskName: "会議資料の準備"}

Controller -> Controller: リクエストバリデーション
Controller -> AppService: createTask(CreateTaskCommand)
Note: CreateTaskCommand {taskName, userId, requestId, timestamp}

AppService -> AppService: 認証・認可チェック
AppService -> AppService: トランザクション開始

AppService -> DomainService: createNewTask(taskName, context)
DomainService -> ValidationService: validate(taskName, context)
ValidationService -> DomainService: ValidationResult {isValid: true}

DomainService -> SecurityService: sanitizeInput(taskName)
SecurityService -> DomainService: SanitizedInput {cleanInput: "会議資料の準備"}

DomainService -> Factory: createTask(sanitizedName)
Factory -> Factory: Taskエンティティ生成
Factory -> DomainService: Task {id: "uuid", name: "会議資料の準備"}

DomainService -> DomainService: TaskCreatedEvent生成
DomainService -> AppService: TaskCreationResult {task, event}

AppService -> Repository: save(task)
Repository -> AppService: Task（永続化済み）

AppService -> EventPublisher: publish(TaskCreatedEvent)
EventPublisher -> AppService: void（非同期）

AppService -> AppService: トランザクション確定
AppService -> Controller: CreateTaskResponse

Controller -> Controller: DTOマッピング
Controller -> Client: HTTP 201 Created
Note: TaskResponseDTO {taskId, taskName, status, createdAt}
```

### 2.2 異常系：バリデーションエラーフロー

```
【シーケンス】
Client -> Controller: POST /api/tasks
Note: CreateTaskRequestDTO {taskName: ""}（空文字）

Controller -> Controller: 基本バリデーション
Controller -> AppService: createTask(CreateTaskCommand)

AppService -> AppService: 認証・認可チェック
AppService -> DomainService: createNewTask("", context)

DomainService -> ValidationService: validate("", context)
ValidationService -> DomainService: ValidationResult {isValid: false, violations: [...]}

DomainService -> AppService: TaskValidationException
Note: BR-001違反：タスク名は必須です

AppService -> AppService: トランザクションロールバック
AppService -> AppService: エラーログ出力
AppService -> Controller: CreateTaskErrorResponse

Controller -> Controller: エラーDTOマッピング
Controller -> Client: HTTP 400 Bad Request
Note: ErrorResponseDTO {errorCode: "VALIDATION_ERROR", message: "タスク名は必須です"}
```

### 2.3 異常系：インフラエラーフロー

```
【シーケンス】
（前半は正常系と同様）

AppService -> Repository: save(task)
Repository -> AppService: InfrastructureException
Note: データベース接続エラー

AppService -> AppService: トランザクションロールバック
AppService -> AppService: エラーログ出力（重要度：ERROR）
AppService -> AppService: アラート送信

AppService -> Controller: CreateTaskErrorResponse
Note: 一般的なエラーメッセージ（セキュリティ考慮）

Controller -> Client: HTTP 500 Internal Server Error
Note: ErrorResponseDTO {errorCode: "INFRASTRUCTURE_ERROR", message: "一時的な問題が発生しました"}
```

## 3. データフロー設計

### 3.1 入力データフロー

```
【HTTPリクエスト → ドメインオブジェクト】

1. クライアント入力
   └→ Raw HTTP Request Body: {"taskName": "会議資料の準備"}

2. プレゼンテーション層
   └→ CreateTaskRequestDTO: {taskName: "会議資料の準備"}
   └→ 基本バリデーション（null チェック、型チェック）

3. アプリケーション層
   └→ CreateTaskCommand: {
        taskName: "会議資料の準備",
        userId: "user-123",
        requestId: "req-456",
        timestamp: "2025-10-22T10:30:00Z"
      }

4. ドメイン層
   └→ TaskCreationContext: {
        userId: UserId("user-123"),
        timestamp: DateTime("2025-10-22T10:30:00Z"),
        requestId: RequestId("req-456")
      }
   └→ TaskName: {
        value: "会議資料の準備"（サニタイズ済み）
      }

5. エンティティ生成
   └→ Task: {
        taskId: TaskId("uuid-789"),
        taskName: TaskName("会議資料の準備"),
        status: TaskStatus("未完了"),
        createdAt: CreatedAt("2025-10-22T10:30:01Z"),
        updatedAt: UpdatedAt("2025-10-22T10:30:01Z")
      }
```

### 3.2 出力データフロー

```
【ドメインオブジェクト → HTTPレスポンス】

1. エンティティ
   └→ Task: {taskId, taskName, status, createdAt, updatedAt}

2. アプリケーション層
   └→ CreateTaskResponse: {
        taskId: "uuid-789",
        taskName: "会議資料の準備",
        status: "未完了",
        createdAt: "2025-10-22T10:30:01Z",
        message: "タスクが正常に追加されました"
      }

3. プレゼンテーション層
   └→ TaskResponseDTO: {
        taskId: "uuid-789",
        taskName: "会議資料の準備",
        status: "未完了",
        createdAt: "2025-10-22T10:30:01Z"
      }

4. HTTPレスポンス
   └→ HTTP 201 Created + JSON Body
```

### 3.3 イベントデータフロー

```
【ドメインイベント → 外部システム】

1. ドメイン層
   └→ TaskCreatedEvent: {
        eventId: "event-abc",
        taskId: "uuid-789",
        taskName: "会議資料の準備",
        userId: "user-123",
        createdAt: "2025-10-22T10:30:01Z",
        occurredAt: "2025-10-22T10:30:01Z"
      }

2. アプリケーション層
   └→ EventPublisher経由で非同期発行

3. インフラ層
   └→ イベントブローカー（例：Kafka、RabbitMQ）
   └→ トピック：task-events

4. 外部システム（Unit2等）
   └→ TaskDataInterface形式で受信：
      {
        taskId: "uuid-789",
        taskName: "会議資料の準備",
        createdAt: "2025-10-22T10:30:01Z",
        status: "未完了"
      }
```

## 4. エラー伝播パターン

### 4.1 エラー種別別の伝播経路

```
【バリデーションエラー】
TaskValidationDomainService
  ↓ ValidationResult（isValid: false）
TaskCreationDomainService
  ↓ TaskValidationException
TaskCreationApplicationService
  ↓ CreateTaskErrorResponse
TaskCreationController
  ↓ HTTP 400 + ErrorResponseDTO

【セキュリティエラー】
TaskSecurityDomainService
  ↓ SecurityCheckResult（isPassed: false）
TaskCreationDomainService
  ↓ TaskSecurityException
TaskCreationApplicationService
  ↓ CreateTaskErrorResponse
TaskCreationController
  ↓ HTTP 422/403 + ErrorResponseDTO

【インフラエラー】
TaskRepository/EventPublisher
  ↓ InfrastructureException
TaskCreationApplicationService
  ↓ CreateTaskErrorResponse（汎用メッセージ）
TaskCreationController
  ↓ HTTP 500 + ErrorResponseDTO
```

### 4.2 エラー情報の変換ルール

```
【詳細度レベル】
1. ドメイン層：詳細なエラー情報（デバッグ用）
2. アプリケーション層：ビジネス的エラー情報
3. プレゼンテーション層：ユーザーフレンドリーなメッセージ
4. クライアント：最小限の安全な情報

【セキュリティ考慮】
- システム内部情報の漏洩防止
- スタックトレースの適切な制御
- エラーログと応答メッセージの分離
```

## 5. 並行性・トランザクション制御

### 5.1 トランザクション境界

```
【トランザクションスコープ】
開始：TaskCreationApplicationService.createTask() メソッド開始時
終了：メソッド正常終了時（commit）または例外発生時（rollback）

【含まれる操作】
1. ドメイン処理（メモリ内操作）
2. TaskRepository.save()（データベース書き込み）
3. イベント発行予約（Outboxパターン）

【除外される操作】
1. 認証・認可チェック（事前処理）
2. 実際のイベント配信（非同期処理）
3. ログ出力（別トランザクション）
```

### 5.2 並行制御戦略

```
【楽観的並行制御】
現在のスコープ：単一エンティティ作成のため楽観的制御で十分
将来の拡張：バージョン番号による楽観的ロック

【分離レベル】
READ_COMMITTED：一般的なOLTPアプリケーションとして適切
理由：幻読み（Phantom Read）の影響は限定的

【デッドロック回避】
- 短時間トランザクション
- 一意制約によるキー競合の最小化
- リトライ機能による自動回復
```

## 6. パフォーマンス特性

### 6.1 レスポンスタイム分析

```
【処理フェーズ別予測時間】
1. HTTP処理・DTO変換：10ms
2. 認証・認可チェック：20ms
3. ドメイン処理（バリデーション・作成）：30ms
4. データベース保存：50ms
5. イベント発行予約：10ms
6. レスポンス生成：10ms

合計予測時間：130ms（正常系）
目標時間：500ms以内（90パーセンタイル）
```

### 6.2 スループット特性

```
【同時リクエスト処理能力】
目標：100リクエスト/秒
制限要因：データベース接続プール（20接続）
1接続あたり：5リクエスト/秒（200ms/リクエスト想定）

【ボトルネック分析】
1. データベースI/O：最大の制限要因
2. バリデーション処理：CPU集約的だが高速
3. メモリ使用量：エンティティは軽量
```

## 7. 監視・観測性

### 7.1 メトリクス収集ポイント

```
【ビジネスメトリクス】
- task_creation_requests_total：作成要求総数
- task_creation_success_total：作成成功総数
- task_creation_errors_total：作成エラー総数（エラー種別別）

【技術メトリクス】
- task_creation_duration_seconds：処理時間
- database_connections_active：アクティブ接続数
- event_publish_queue_size：イベント発行キューサイズ

【収集場所】
- Controller：HTTPメトリクス
- ApplicationService：ビジネスメトリクス
- Repository：データアクセスメトリクス
- EventPublisher：イベント配信メトリクス
```

### 7.2 ログ出力設計

```
【構造化ログ例】
{
  "timestamp": "2025-10-22T10:30:00.123Z",
  "level": "INFO",
  "requestId": "req-456",
  "userId": "user-123",
  "operation": "task_creation",
  "phase": "domain_processing",
  "message": "Task creation started",
  "metadata": {
    "taskName": "会議資料の準備",
    "sanitized": true
  }
}

【ログ出力タイミング】
- 処理開始時（INFO）
- バリデーション完了時（DEBUG）
- エンティティ作成時（INFO）
- 永続化完了時（INFO）
- エラー発生時（ERROR）
- 処理完了時（INFO）
```

## 8. セキュリティ考慮事項

### 8.1 入力検証の多層防御

```
【検証レイヤー】
1. プレゼンテーション層
   - HTTPレベルの制約（Content-Type、サイズ制限）
   - DTOレベルの構造チェック

2. アプリケーション層
   - 認証・認可の確認
   - ビジネスルールレベルの制約

3. ドメイン層
   - エンティティ不変条件の確認
   - セキュリティドメインサービスによる高度なチェック

4. インフラ層
   - データベース制約
   - SQL インジェクション防止
```

### 8.2 情報漏洩防止

```
【機密情報の取り扱い】
- エラーメッセージ：技術的詳細を隠蔽
- ログ出力：個人情報のマスキング
- スタックトレース：内部構造の非開示

【監査証跡】
- すべてのタスク作成要求をログ記録
- 失敗要求の詳細分析用情報保持
- セキュリティイベントの即座通知
```

## 9. テスト戦略

### 9.1 テスト対象とテストレベル

```
【単体テスト】
- 各ドメインサービス
- エンティティ・値オブジェクト
- アプリケーションサービス（モック使用）

【統合テスト】
- データベース連携
- イベント発行・購読
- HTTP エンドポイント

【E2Eテスト】
- 実際のHTTPリクエストから永続化まで
- エラーハンドリングの確認
- パフォーマンス要件の確認
```

### 9.2 テストデータ管理

```
【テストシナリオ】
1. 正常系：有効なタスク名での作成
2. バリデーションエラー：空文字、長すぎる文字列
3. セキュリティエラー：悪意ある入力
4. インフラエラー：データベース障害、ネットワーク障害
5. 並行性テスト：同時リクエスト処理

【テスト環境】
- 専用テストデータベース
- モックイベントブローカー
- テスト用認証・認可サービス
```

## 10. 運用・保守性

### 10.1 デプロイメント考慮事項

```
【Blue-Green デプロイメント対応】
- データベーススキーマの後方互換性
- イベントスキーマのバージョニング
- 設定の外部化

【ヘルスチェック】
- データベース接続確認
- イベントブローカー接続確認
- 依存サービスの稼働確認
```

### 10.2 トラブルシューティング

```
【問題診断のための情報】
- リクエストID による追跡
- 構造化ログによる検索
- メトリクスによる傾向分析
- 分散トレーシング（将来実装）

【自動回復機能】
- データベースコネクション再接続
- イベント発行のリトライ
- サーキットブレーカー（将来実装）
```

---

**次フェーズへの引き継ぎ**:
- コンポーネント間相互作用の詳細設計完了
- データフローとエラー伝播パターン定義完了
- パフォーマンス・セキュリティ要件の具体化完了
- テスト・運用戦略の策定完了