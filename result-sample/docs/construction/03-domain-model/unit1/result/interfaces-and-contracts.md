# インターフェース・契約定義書 - Unit1: タスク作成機能

## 作成情報

- **作成日**: 2025-10-22
- **設計対象**: タスク作成機能のインターフェースと契約
- **分析フェーズ**: フェーズ4（インフラストラクチャ層設計）
- **参照元**: アプリケーションサービス設計書、ドメインエンティティ設計書

## 1. リポジトリインターフェース設計

### 1.1 TaskRepository インターフェース

```
目的: Taskエンティティの永続化に関する契約定義
責務: データ永続化層とドメイン層の分離

インターフェース定義:
interface TaskRepository {
    // タスクの保存（作成・更新）
    save(task: Task): Promise<Task>

    // IDによるタスク検索
    findById(taskId: TaskId): Promise<Task | null>

    // ユーザーIDによるタスク検索（将来拡張用）
    findByUserId(userId: UserId): Promise<Task[]>

    // 存在確認
    exists(taskId: TaskId): Promise<boolean>

    // トランザクション境界内での操作
    saveInTransaction(task: Task, transaction: Transaction): Promise<Task>
}

設計原則:
- 依存性逆転の原則に従い、ドメイン層がインフラ層に依存しない
- 永続化技術に依存しない抽象的なインターフェース
- 集約境界を尊重した操作セット
```

### 1.2 データ永続化の契約

#### 1.2.1 save操作の契約

```
操作: save(task: Task): Promise<Task>
目的: Taskエンティティの永続化

事前条件:
- task は有効なTaskエンティティである
- task のすべての不変条件が満たされている
- トランザクションが開始されている（推奨）

事後条件:
- taskがデータストアに永続化される
- 新規作成時はtaskIdが確定する
- 更新時はupdatedAtが更新される
- 保存されたTaskエンティティが返される

例外:
- TaskPersistenceException: 永続化処理失敗
- TaskDuplicateException: 重複キー制約違反（稀）
- InfrastructureException: データベース接続エラー等

パフォーマンス要件:
- 実行時間: 100ms以内（90パーセンタイル）
- 同時実行: デッドロック回避機能
- 制約チェック: データベースレベルでの整合性保証
```

#### 1.2.2 findById操作の契約

```
操作: findById(taskId: TaskId): Promise<Task | null>
目的: 指定されたIDのTaskエンティティを取得

事前条件:
- taskId は有効なTaskIdである
- taskId はnullでない

事後条件:
- 対象のTaskが存在する場合、完全なTaskエンティティを返す
- 対象のTaskが存在しない場合、nullを返す
- 返されるTaskは不変条件を満たす

例外:
- TaskNotFoundException: 指定されたIDが不正形式
- InfrastructureException: データアクセスエラー

パフォーマンス要件:
- 実行時間: 50ms以内（平均）
- キャッシュ: 頻繁にアクセスされるデータのキャッシュ機能
- インデックス: taskIdに対する一意インデックス
```

### 1.3 トランザクション境界の設計

#### 1.3.1 トランザクション管理インターフェース

```
interface TransactionManager {
    // トランザクション開始
    beginTransaction(): Promise<Transaction>

    // トランザクション確定
    commit(transaction: Transaction): Promise<void>

    // トランザクションロールバック
    rollback(transaction: Transaction): Promise<void>

    // トランザクション実行（try-with-resources パターン）
    executeInTransaction<T>(operation: (tx: Transaction) => Promise<T>): Promise<T>
}

Transaction抽象化:
interface Transaction {
    readonly id: string
    readonly status: TransactionStatus
    readonly startTime: DateTime

    // 手動制御用メソッド
    commit(): Promise<void>
    rollback(): Promise<void>
    isActive(): boolean
}

TransactionStatus列挙:
enum TransactionStatus {
    ACTIVE = "ACTIVE",
    COMMITTED = "COMMITTED",
    ROLLED_BACK = "ROLLED_BACK",
    FAILED = "FAILED"
}
```

#### 1.2.2 分散トランザクション考慮

```
現在のスコープ: 単一データベース内でのACID特性保証
将来の拡張:
- Sagaパターンによる分散トランザクション
- 補償トランザクション（Compensating Transaction）
- 結果整合性（Eventual Consistency）

実装方針:
- 現時点では単一データベーストランザクション
- インターフェースは将来の分散トランザクションに対応可能な設計
- ユニット間の整合性は非同期イベントで実現
```

## 2. イベント発行インターフェース

### 2.1 EventPublisher インターフェース

```
目的: ドメインイベントの発行に関する契約定義
責務: イベント発行とイベントブローカーとの分離

インターフェース定義:
interface EventPublisher {
    // 単一イベント発行
    publish<T extends DomainEvent>(event: T): Promise<void>

    // 複数イベント一括発行
    publishBatch(events: DomainEvent[]): Promise<void>

    // トランザクション確定後の発行予約
    publishAfterCommit<T extends DomainEvent>(event: T, transaction: Transaction): Promise<void>

    // 発行状況の確認
    getPublishStatus(eventId: string): Promise<PublishStatus>
}

設計原則:
- Outboxパターンによる確実な配信保証
- At-least-once配信セマンティクス
- 冪等性を考慮した重複処理対応
```

### 2.2 イベント配信の契約

#### 2.2.1 publish操作の契約

```
操作: publish<T extends DomainEvent>(event: T): Promise<void>
目的: ドメインイベントを他の境界コンテキストに配信

事前条件:
- event は有効なDomainEventインスタンスである
- event のすべての必須属性が設定されている
- イベントスキーマが適切である

事後条件:
- イベントがイベントストアに永続化される
- 配信対象のサブスクライバーにイベントが配信される
- 配信確認が取得される

例外:
- EventValidationException: イベント妥当性チェック失敗
- EventPublishException: 配信処理失敗
- InfrastructureException: イベントブローカー接続エラー

配信保証:
- 配信確認: At-least-once セマンティクス
- リトライ機能: 指数バックオフによる自動リトライ
- Dead Letter Queue: 配信失敗時の証跡管理
```

#### 2.2.2 イベント配信戦略

```
配信パターン:
1. 即座配信（同期）: 重要度が高く遅延許容度が低いイベント
2. 非同期配信（推奨）: 一般的なドメインイベント
3. バッチ配信: 大量イベントの効率的配信

配信先管理:
- トピックベースルーティング
- サブスクライバー登録管理
- 動的サブスクライバー追加/削除

監視・運用:
- 配信遅延の監視
- 配信失敗の通知
- スループット・レイテンシの測定
```

## 3. 外部インターフェース設計

### 3.1 他ユニットとのデータ交換インターフェース

#### 3.1.1 TaskDataInterface詳細化

```
目的: Unit2（タスク表示機能）との統一データ形式定義
形式: JSON Schema準拠のデータ交換形式

データ構造定義:
interface TaskDataInterface {
    taskId: string           // UUID形式の一意識別子
    taskName: string         // タスク名（サニタイズ済み）
    createdAt: string        // ISO8601形式の作成日時
    status: string           // タスクステータス（初期値："未完了"）

    // メタデータ（将来拡張用）
    metadata?: {
        version: string      // データ形式バージョン
        source: string       // データ作成元ユニット識別子
        lastModified: string // 最終更新日時
    }
}

制約条件:
- taskId: 必須、UUID v4形式、36文字固定
- taskName: 必須、1-100文字、HTMLエスケープ済み
- createdAt: 必須、ISO8601形式（例: "2025-10-22T10:30:00.000Z"）
- status: 必須、事前定義値のみ（"未完了", "完了", "保留"等）

バージョニング戦略:
- メジャーバージョン: 後方互換性を破る変更
- マイナーバージョン: 後方互換性を保つ機能追加
- パッチバージョン: バグ修正
```

#### 3.1.2 データ変換インターフェース

```
目的: ドメインエンティティと外部データ形式の変換

インターフェース定義:
interface TaskDataConverter {
    // ドメインエンティティから外部形式への変換
    toTaskDataInterface(task: Task): TaskDataInterface

    // 外部形式からドメインエンティティへの変換（将来拡張用）
    fromTaskDataInterface(data: TaskDataInterface): Task

    // バリデーション機能
    validateTaskDataInterface(data: TaskDataInterface): ValidationResult

    // バージョン互換性チェック
    isCompatibleVersion(version: string): boolean
}

変換ルール:
1. TaskId → taskId: UUID文字列への変換
2. TaskName → taskName: 値の取得とエスケープ確認
3. CreatedAt → createdAt: ISO8601形式への変換
4. TaskStatus → status: 文字列表現への変換
5. メタデータの自動生成

エラーハンドリング:
- 変換不可能な値: DataConversionException
- スキーマ不適合: SchemaValidationException
- バージョン不一致: VersionMismatchException
```

### 3.2 外部システムインターフェース

#### 3.2.1 ログ出力インターフェース

```
目的: 統一されたログ出力機能の提供

インターフェース定義:
interface Logger {
    // レベル別ログ出力
    info(message: string, context?: LogContext): void
    warn(message: string, context?: LogContext): void
    error(message: string, error?: Error, context?: LogContext): void
    debug(message: string, context?: LogContext): void

    // 構造化ログ出力
    logStructured(level: LogLevel, data: StructuredLogData): void

    // メトリクス出力
    logMetric(name: string, value: number, tags?: Tags): void
}

LogContext定義:
interface LogContext {
    requestId?: string
    userId?: string
    taskId?: string
    operation?: string
    duration?: number
    additionalData?: Record<string, unknown>
}

設計原則:
- 構造化ログによる検索・分析容易性
- 個人情報の適切なマスキング
- パフォーマンスへの影響最小化
```

#### 3.2.2 設定管理インターフェース

```
目的: アプリケーション設定の外部化と管理

インターフェース定義:
interface ConfigurationProvider {
    // 文字列設定値の取得
    getString(key: string, defaultValue?: string): string

    // 数値設定値の取得
    getNumber(key: string, defaultValue?: number): number

    // 真偽値設定値の取得
    getBoolean(key: string, defaultValue?: boolean): boolean

    // 複合設定値の取得
    getObject<T>(key: string, schema: Schema<T>): T

    // 設定値の更新通知
    onConfigChange(key: string, callback: (value: unknown) => void): void
}

設定項目例:
- database.connectionString: データベース接続文字列
- taskCreation.maxRetries: 作成処理最大リトライ回数
- validation.maxTaskNameLength: タスク名最大文字数
- security.sanitization.policy: サニタイゼーションポリシー
- logging.level: ログレベル

セキュリティ考慮:
- 機密情報の暗号化
- アクセス権の制限
- 監査ログの記録
```

## 4. データアクセス層の設計

### 4.1 データマッピング戦略

```
マッピング方式: 半自動マッピング（Data Mapper パターン）

エンティティ ⟷ データベーステーブル マッピング:
Task Entity ⟷ tasks テーブル

マッピング詳細:
- TaskId      ⟷ task_id (VARCHAR(36), PRIMARY KEY)
- TaskName    ⟷ task_name (VARCHAR(100), NOT NULL)
- TaskStatus  ⟷ status (VARCHAR(20), NOT NULL)
- CreatedAt   ⟷ created_at (TIMESTAMP, NOT NULL)
- UpdatedAt   ⟷ updated_at (TIMESTAMP, NOT NULL)

制約定義:
- PRIMARY KEY: task_id
- INDEX: user_id（将来拡張用）
- CHECK制約: task_nameの長さ制限
- DEFAULT値: statusの初期値設定
```

### 4.2 データベーススキーマ定義

```
テーブル定義（概念レベル）:
CREATE TABLE tasks (
    task_id VARCHAR(36) PRIMARY KEY,
    task_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT '未完了',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    -- 制約
    CONSTRAINT chk_task_name_length
        CHECK (LENGTH(task_name) >= 1 AND LENGTH(task_name) <= 100),
    CONSTRAINT chk_status_value
        CHECK (status IN ('未完了', '完了', '保留'))
);

インデックス定義:
- PRIMARY INDEX: task_id（一意性保証）
- COMPOSITE INDEX: status, created_at（将来のクエリ最適化用）

パフォーマンス考慮:
- 自動統計更新
- パーティショニング（将来的な大量データ対応）
- 適切なバキューム・アナライズスケジュール
```

## 5. セキュリティインターフェース

### 5.1 認証・認可インターフェース

```
目的: セキュリティ関連機能の抽象化

インターフェース定義:
interface SecurityService {
    // 認証
    authenticate(token: string): Promise<AuthenticationResult>

    // 認可
    authorize(user: User, permission: Permission): Promise<boolean>

    // トークン検証
    validateToken(token: string): Promise<TokenValidationResult>

    // セッション管理
    getSessionInfo(token: string): Promise<SessionInfo>
}

AuthenticationResult:
interface AuthenticationResult {
    isAuthenticated: boolean
    user?: User
    permissions?: Permission[]
    expiresAt?: DateTime
    error?: AuthenticationError
}

Permission定義:
enum Permission {
    TASK_CREATE = "TASK_CREATE",
    TASK_READ = "TASK_READ",
    TASK_UPDATE = "TASK_UPDATE",
    TASK_DELETE = "TASK_DELETE"
}
```

### 5.2 データ保護インターフェース

```
目的: 個人情報・機密情報の保護

インターフェース定義:
interface DataProtectionService {
    // データマスキング
    maskSensitiveData(data: string, type: DataType): string

    // データ暗号化
    encrypt(plaintext: string, context: EncryptionContext): Promise<string>

    // データ復号化
    decrypt(ciphertext: string, context: EncryptionContext): Promise<string>

    // 監査ログ記録
    auditDataAccess(operation: DataOperation, context: AuditContext): void
}

適用対象:
- ユーザー個人情報（将来拡張時）
- システム内部情報
- ログ出力時の機密データ
```

## 6. 監視・メトリクスインターフェース

### 6.1 アプリケーションメトリクス

```
目的: システム稼働状況の可視化

インターフェース定義:
interface MetricsCollector {
    // カウンタメトリクス
    incrementCounter(name: string, tags?: Tags): void

    // ゲージメトリクス
    recordGauge(name: string, value: number, tags?: Tags): void

    // ヒストグラムメトリクス
    recordHistogram(name: string, value: number, tags?: Tags): void

    // タイマーメトリクス
    measureTime<T>(name: string, operation: () => Promise<T>, tags?: Tags): Promise<T>
}

収集対象メトリクス:
- task_creation_count: タスク作成数
- task_creation_duration: 作成処理時間
- task_creation_errors: 作成エラー数
- validation_failures: バリデーション失敗数
- database_connection_pool: コネクションプール使用状況
```

### 6.2 ヘルスチェックインターフェース

```
目的: システム稼働状況の監視

インターフェース定義:
interface HealthChecker {
    // システム全体のヘルスチェック
    checkHealth(): Promise<HealthStatus>

    // 個別コンポーネントのヘルスチェック
    checkComponentHealth(component: string): Promise<ComponentHealth>

    // ヘルスチェック結果の履歴取得
    getHealthHistory(duration: Duration): Promise<HealthHistory[]>
}

チェック対象:
- データベース接続状況
- イベントブローカー接続状況
- 外部サービス接続状況
- システムリソース使用状況
```

## 7. テストサポートインターフェース

### 7.1 テストデータ管理

```
目的: テスト実行時のデータ管理支援

インターフェース定義:
interface TestDataManager {
    // テストデータセットアップ
    setupTestData(scenario: TestScenario): Promise<TestDataSet>

    // テストデータクリーンアップ
    cleanupTestData(dataSet: TestDataSet): Promise<void>

    // テスト用モックデータ生成
    generateMockData<T>(type: DataType, count: number): T[]

    // テストデータベースの初期化
    initializeTestDatabase(): Promise<void>
}

テストシナリオ例:
- VALID_TASK_CREATION: 正常なタスク作成テスト用
- INVALID_INPUT_VALIDATION: 不正入力バリデーションテスト用
- SECURITY_CONSTRAINT_TEST: セキュリティ制約テスト用
```

### 7.2 モックインターフェース

```
目的: 単体テスト時の外部依存モック化

提供モック:
- MockTaskRepository: リポジトリのモック実装
- MockEventPublisher: イベント発行のモック実装
- MockSecurityService: セキュリティサービスのモック実装
- MockLogger: ログ出力のモック実装

モック機能:
- 戻り値の設定
- 例外発生の設定
- 呼び出し回数の検証
- 引数の検証
```

## 8. 実装ガイドライン

### 8.1 インターフェース実装の原則

```
1. 単一責任の原則: 各インターフェースは明確で単一の責任を持つ
2. 開放閉鎖の原則: 拡張に対して開いており、修正に対して閉じている
3. 依存性逆転の原則: 具象ではなく抽象に依存する
4. インターフェース分離の原則: 使用しないメソッドへの依存を強制しない
5. DRY原則: 同じ契約定義の重複を避ける
```

### 8.2 エラーハンドリング設計

```
例外設計方針:
- チェック例外: 回復可能なビジネスエラー
- 非チェック例外: プログラミングエラー・システムエラー
- カスタム例外: ドメイン固有のエラー情報

例外情報の内容:
- エラーコード: 機械可読な識別子
- エラーメッセージ: 人間可読な説明文
- エラー詳細: デバッグ用詳細情報
- コンテキスト情報: エラー発生時の状況
```

---

**次フェーズへの引き継ぎ**:
- 全インターフェース・契約定義完了
- データアクセス層設計完了
- セキュリティインターフェース定義完了
- テスト支援機能定義完了