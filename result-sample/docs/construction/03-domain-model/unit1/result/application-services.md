# アプリケーションサービス設計書 - Unit1: タスク作成機能

## 作成情報

- **作成日**: 2025-10-22
- **設計対象**: タスク作成機能のアプリケーションサービス
- **分析フェーズ**: フェーズ3（アプリケーションサービス設計）
- **参照元**: ドメインエンティティ設計書、ドメインサービス設計書

## 1. アプリケーションサービス概要

### 1.1 アプリケーション層の責務

- ユースケースの実行調整
- トランザクション境界の管理
- ドメインサービスとインフラストラクチャの統合
- プレゼンテーション層とドメイン層の分離
- 認証・認可の実装
- ログ出力とモニタリング

### 1.2 設計原則

- **単一責任の原則**: 1つのユースケースに1つのアプリケーションサービス
- **依存性逆転の原則**: インフラストラクチャ層への依存はインターフェース経由
- **トランザクション管理**: アプリケーションサービスでトランザクション境界を制御
- **ドメインロジック分離**: ビジネスロジックはドメイン層に委譲

## 2. TaskCreationApplicationService

### 2.1 サービス概要

**サービス名**: TaskCreationApplicationService
**責務**: タスク作成ユースケースの実行統括
**トランザクション境界**: 単一のタスク作成処理

### 2.2 依存関係

```
TaskCreationApplicationService の依存関係:

インターフェース:
├─→ TaskRepository（永続化）
├─→ TaskCreationDomainService（ドメインロジック）
├─→ Logger（ログ出力）
├─→ EventPublisher（イベント発行）
└─→ TransactionManager（トランザクション管理）

実装クラス（インジェクション）:
├─→ TaskRepositoryImpl
├─→ TaskCreationDomainServiceImpl
├─→ ApplicationLogger
├─→ DomainEventPublisher
└─→ TransactionManagerImpl
```

### 2.3 操作定義

#### 2.3.1 createTask操作

```
操作名: createTask
目的: 新しいタスクを作成する（US-001, US-002対応）

シグネチャ:
createTask(command: CreateTaskCommand): CreateTaskResponse

処理フロー:
1. [事前処理] コマンド検証とログ出力
2. [認証] ユーザー認証状態の確認
3. [認可] タスク作成権限の確認
4. [トランザクション開始]
5. [ドメイン処理] TaskCreationDomainService.createNewTask()
6. [永続化] TaskRepository.save()
7. [イベント発行] EventPublisher.publish(TaskCreatedEvent)
8. [トランザクション確定]
9. [事後処理] レスポンス生成とログ出力

成功時のフロー:
CreateTaskCommand → [検証] → [ドメイン処理] → [永続化] → [イベント発行] → CreateTaskResponse

エラー時のフロー:
Exception → [ロールバック] → [エラーログ] → [エラーレスポンス] → CreateTaskErrorResponse

事前条件:
- 有効なCreateTaskCommandが提供される
- ユーザーが認証済みである
- タスク作成権限を持つ

事後条件:
- タスクが永続化される
- TaskCreatedEventが発行される
- 成功/失敗レスポンスが返される

例外:
- TaskCreationException: 作成処理失敗
- UnauthorizedException: 認証失敗
- ForbiddenException: 認可失敗
- InfrastructureException: インフラ障害
```

## 3. コマンドとクエリの設計

### 3.1 CreateTaskCommand

```
目的: タスク作成要求を表現するコマンドオブジェクト

属性:
- taskName: string（作成するタスク名）
- userId: string（作成者ID）
- requestId: string（リクエスト追跡ID）
- timestamp: DateTime（要求時刻）
- clientInfo: ClientInfo（クライアント情報）

制約:
- taskName: 必須、100文字以内、nullまたは空文字不可
- userId: 必須、有効なユーザーID形式
- requestId: 必須、UUID形式
- timestamp: 必須、現在時刻以前
- clientInfo: 必須

バリデーション:
- 構造的妥当性の検証
- ビジネスルール適用前の基本チェック
- セキュリティ制約の事前確認

変換:
- TaskCreationContextへの変換
- ドメインサービス呼び出し用パラメータ生成
```

### 3.2 CreateTaskResponse

```
目的: タスク作成処理の成功結果を表現

属性:
- taskId: string（作成されたタスクのID）
- taskName: string（確定したタスク名）
- status: string（初期ステータス）
- createdAt: DateTime（作成日時）
- message: string（成功メッセージ）
- requestId: string（要求追跡ID）

制約:
- すべての属性が非null
- taskIdはUUID形式
- messageはユーザーフレンドリー

用途:
- プレゼンテーション層への結果通知
- 成功フィードバックの提供
- 監査ログの生成
```

### 3.3 CreateTaskErrorResponse

```
目的: タスク作成処理の失敗結果を表現

属性:
- errorCode: string（エラーコード）
- errorMessage: string（エラーメッセージ）
- details: ErrorDetail[]（詳細エラー情報）
- timestamp: DateTime（エラー発生時刻）
- requestId: string（要求追跡ID）

エラーコード分類:
- VALIDATION_ERROR: バリデーションエラー
- SECURITY_ERROR: セキュリティエラー
- BUSINESS_RULE_VIOLATION: ビジネスルール違反
- INFRASTRUCTURE_ERROR: インフラエラー
- UNKNOWN_ERROR: 不明なエラー

制約:
- errorCodeは事前定義済みの値
- errorMessageはユーザーフレンドリー
- detailsはトラブルシューティング用詳細情報

用途:
- エラーハンドリング
- ユーザーへの適切なフィードバック
- システム監視とアラート
```

## 4. イベント設計

### 4.1 TaskCreatedEvent

```
目的: タスク作成完了を他の境界コンテキストに通知

属性:
- eventId: string（イベント一意ID）
- taskId: string（作成されたタスクID）
- taskName: string（作成されたタスク名）
- userId: string（作成者ID）
- createdAt: DateTime（タスク作成日時）
- occurredAt: DateTime（イベント発生日時）
- version: number（イベントバージョン）

メタデータ:
- eventType: "TaskCreated"
- aggregateType: "Task"
- aggregateId: taskId
- causationId: requestId
- correlationId: ビジネス処理ID

配信先:
- タスク表示機能（Unit2）
- 通知サービス（将来拡張）
- 分析サービス（将来拡張）
- 監査ログサービス

配信保証:
- At-least-once配信
- 重複処理対応（idempotent）
- 失敗時のリトライ機能
```

### 4.2 イベント発行戦略

```
発行タイミング: トランザクション確定後
発行方法: 非同期（パフォーマンス考慮）
失敗時の対応:
- リトライ機能（指数バックオフ）
- Dead Letter Queue
- 管理者への通知

配信順序保証:
- 同一集約内では順序保証
- 異なる集約間では順序非保証（結果整合性）

パフォーマンス要件:
- イベント発行遅延: 100ms以内
- 配信成功率: 99.9%以上
- リトライ回数: 最大3回
```

## 5. エラーハンドリング戦略

### 5.1 エラー分類と対応

```
【バリデーションエラー】
原因: 入力データの不正
対応:
- 詳細なエラーメッセージを返却
- HTTP 400 Bad Request
- リトライ不要

【ビジネスルール違反】
原因: ドメインルール違反
対応:
- ビジネス的なエラーメッセージを返却
- HTTP 422 Unprocessable Entity
- ユーザー操作で修正可能

【認証・認可エラー】
原因: セキュリティ制約違反
対応:
- 最小限のエラー情報のみ返却
- HTTP 401/403
- セキュリティログに記録

【インフラエラー】
原因: システム障害
対応:
- 汎用エラーメッセージ
- HTTP 500 Internal Server Error
- アラート発行、リトライ対象
```

### 5.2 トランザクション管理

```
トランザクション境界: アプリケーションサービスメソッド単位

成功時:
1. ドメイン処理実行
2. データ永続化
3. トランザクション確定
4. イベント発行

失敗時:
1. 例外キャッチ
2. トランザクションロールバック
3. エラーログ出力
4. エラーレスポンス生成

分散トランザクション:
現在のスコープでは単一データベースのため考慮不要
将来的にSagaパターンの導入を検討
```

## 6. ログ出力戦略

### 6.1 ログレベル定義

```
【INFO】処理開始・終了、成功時の結果
例: "Task creation started for user: {userId}"
    "Task created successfully: {taskId}"

【WARN】警告レベルの問題、回復可能なエラー
例: "Validation warning: task name contains special characters"
    "Retry attempt 2/3 for event publishing"

【ERROR】システムエラー、業務処理失敗
例: "Task creation failed: {errorMessage}"
    "Database connection failed during task creation"

【DEBUG】詳細な処理情報（開発・テスト環境のみ）
例: "Domain service called with parameters: {params}"
    "Event publishing configuration: {config}"
```

### 6.2 ログ情報の構造化

```
必須情報:
- timestamp: ログ出力時刻
- level: ログレベル
- requestId: リクエスト追跡ID
- userId: ユーザーID
- operation: 実行中の操作名
- message: ログメッセージ

オプション情報:
- taskId: 関連するタスクID
- duration: 処理時間
- errorCode: エラーコード
- stackTrace: スタックトレース（ERROR時）

フォーマット: 構造化JSON形式
出力先: ファイル + 監視システム
```

## 7. パフォーマンス要件

### 7.1 レスポンス時間目標

```
正常処理: 500ms以内（90パーセンタイル）
バリデーションエラー: 100ms以内
システムエラー: 1秒以内（フェイルファスト）

測定対象:
- アプリケーションサービス処理時間
- データベース応答時間
- イベント発行時間
```

### 7.2 スループット要件

```
同時実行数: 100リクエスト/秒
ピーク時間帯: 平常時の3倍まで対応
データベース接続: コネクションプール使用（最大20接続）
```

## 8. セキュリティ要件

### 8.1 認証・認可

```
認証方式: JWT トークンベース認証
認可方式: ロールベースアクセス制御（RBAC）

必要な権限:
- TASK_CREATE: タスク作成権限
- USER_ACTIVE: アクティブユーザー権限

チェックポイント:
1. JWTトークンの妥当性検証
2. ユーザーアクティブ状態確認
3. TASK_CREATE権限の確認
4. レート制限チェック
```

### 8.2 入力検証

```
検証レベル:
1. 構造的検証（Command内）
2. ビジネス検証（ドメインサービス内）
3. セキュリティ検証（セキュリティサービス内）

防御対象:
- SQLインジェクション
- XSSアタック
- CSRF攻撃
- 大量データ攻撃
```

## 9. テスト戦略

### 9.1 単体テスト

```
テスト対象:
- コマンド/レスポンスの妥当性
- 正常フロー処理
- 各種エラーハンドリング
- トランザクション制御

モック対象:
- TaskRepository
- TaskCreationDomainService
- EventPublisher
- Logger
```

### 9.2 統合テスト

```
テスト対象:
- エンドツーエンドの処理フロー
- データベース連携
- イベント発行・購読
- エラー伝播パターン

テスト環境:
- テスト用データベース
- イベントブローカー
- ログ収集システム
```

## 10. 監視・メトリクス

### 10.1 ビジネスメトリクス

```
- タスク作成成功率
- 平均作成処理時間
- エラー種別の発生頻度
- ユーザー別作成数
```

### 10.2 技術メトリクス

```
- CPU/メモリ使用率
- データベース接続数
- スレッドプール使用状況
- GCの実行頻度と時間
```

## 11. 他ユニットとの連携

### 11.1 下流への情報提供

```
提供先: Unit2（タスク表示機能）
提供方法: TaskCreatedEventによる非同期通知
提供データ: TaskDataInterface準拠の形式

データ形式:
- taskId: string
- taskName: string
- createdAt: datetime
- status: string
```

### 11.2 上流からの要求受付

```
受付元: プレゼンテーション層
受付形式: CreateTaskCommand
処理結果: CreateTaskResponse/CreateTaskErrorResponse

インターフェース契約:
- 入力検証の責務分担
- エラーレスポンス形式の統一
- HTTP ステータスコードの対応
```

---

**次フェーズへの引き継ぎ**:
- アプリケーションサービス設計完了
- コマンド・イベント設計完了
- エラーハンドリング戦略確定
- 非機能要件の具体化完了