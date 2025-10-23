# ドメインサービス設計書 - Unit1: タスク作成機能

## 作成情報

- **作成日**: 2025-10-22
- **設計対象**: タスク作成機能のドメインサービス
- **分析フェーズ**: フェーズ2-2（ドメインサービスの識別）
- **参照元**: 要件分析書、ドメインエンティティ設計書

## 1. ドメインサービス概要

### 1.1 ドメインサービスの識別基準

以下の条件を満たすビジネスロジックをドメインサービスとして抽出：

- 単一のエンティティに属さない複雑なビジネスルール
- 複数のエンティティや値オブジェクトにまたがる処理
- 外部システムとの協調が必要な処理
- エンティティの純粋性を保つために分離すべき処理

### 1.2 識別されたドメインサービス

1. **TaskCreationDomainService** - タスク作成処理の統括
2. **TaskValidationDomainService** - 高度なバリデーション処理
3. **TaskSecurityDomainService** - セキュリティ関連処理

## 2. TaskCreationDomainService

### 2.1 サービス概要

**サービス名**: TaskCreationDomainService
**責務**: タスク作成プロセス全体の調整とビジネスルールの実施
**スコープ**: Task集約内のビジネスロジック

### 2.2 操作定義

#### 2.2.1 createNewTask操作

```
操作名: createNewTask
目的: 新しいタスクを作成し、ビジネスルールを適用する

シグネチャ:
createNewTask(
  taskName: string,
  creationContext: TaskCreationContext
): TaskCreationResult

処理フロー:
1. 入力パラメータの基本検証
2. TaskValidationDomainServiceを使用したバリデーション
3. TaskSecurityDomainServiceを使用したセキュリティ処理
4. TaskFactoryを使用したエンティティ作成
5. TaskCreatedEventの生成
6. 結果の返却

事前条件:
- taskNameが提供されている
- creationContextが有効である

事後条件:
- 有効なTaskエンティティが作成される
- TaskCreatedEventが生成される
- 全てのビジネスルールが満たされる

例外:
- TaskValidationException: バリデーション失敗
- TaskSecurityException: セキュリティ違反
- TaskCreationException: 作成処理失敗
```

#### 2.2.2 TaskCreationContext（値オブジェクト）

```
目的: タスク作成時のコンテキスト情報を保持

属性:
- userId: UserId（作成者ID）
- timestamp: DateTime（作成要求時刻）
- clientInfo: ClientInfo（クライアント情報）
- requestId: RequestId（リクエスト追跡ID）

制約:
- すべての属性がnull不可
- timestampは現在時刻以前である

振る舞い:
- 等価性比較
- コンテキスト妥当性検証
```

#### 2.2.3 TaskCreationResult（値オブジェクト）

```
目的: タスク作成処理の結果を格納

属性:
- task: Task（作成されたタスク）
- event: TaskCreatedEvent（生成されたイベント）
- createdAt: DateTime（実際の作成時刻）
- success: boolean（成功フラグ）

制約:
- success=trueの場合、taskとeventがnull不可
- createdAtは作成処理実行時刻

振る舞い:
- 成功/失敗判定
- 結果の抽出
```

## 3. TaskValidationDomainService

### 3.1 サービス概要

**サービス名**: TaskValidationDomainService
**責務**: タスク作成時の高度なバリデーションロジック
**理由**: エンティティの責務範囲を超える複雑なバリデーション

### 3.2 操作定義

#### 3.2.1 validateTaskCreation操作

```
操作名: validateTaskCreation
目的: タスク作成時の包括的バリデーション

シグネチャ:
validateTaskCreation(
  taskName: string,
  context: TaskCreationContext
): ValidationResult

バリデーション項目:
1. 基本バリデーション
   - null/空文字チェック（BR-001）
   - 文字数制限チェック（BR-004）

2. セキュリティバリデーション
   - 特殊文字パターンチェック（BR-005）
   - XSS攻撃パターン検出
   - SQLインジェクション パターン検出

3. ビジネスルールバリデーション
   - 予約語チェック
   - 不適切なコンテンツフィルタ

4. コンテキストバリデーション
   - 作成権限の確認
   - レート制限チェック
   - 時間制約チェック

戻り値: ValidationResult
- isValid: boolean
- violations: ValidationViolation[]
- severity: ValidationSeverity

例外なし（結果オブジェクトでエラー情報を返却）
```

#### 3.2.2 ValidationResult（値オブジェクト）

```
目的: バリデーション結果の詳細情報を提供

属性:
- isValid: boolean（バリデーション成功/失敗）
- violations: ValidationViolation[]（違反詳細）
- validatedAt: DateTime（バリデーション実行時刻）

制約:
- isValid=falseの場合、violationsが空でない
- validatedAtがnull不可

振る舞い:
- 違反情報の取得
- エラーメッセージの整形
- 重要度別の違反フィルタリング
```

#### 3.2.3 ValidationViolation（値オブジェクト）

```
目的: 個別のバリデーション違反情報

属性:
- ruleId: string（違反したルールID）
- message: string（エラーメッセージ）
- severity: ValidationSeverity（重要度）
- fieldName: string（対象フィールド名）

制約:
- すべての属性がnull不可
- messageはユーザーフレンドリーである

振る舞い:
- メッセージの国際化対応
- 重要度に基づく表示制御
```

## 4. TaskSecurityDomainService

### 4.1 サービス概要

**サービス名**: TaskSecurityDomainService
**責務**: タスク作成時のセキュリティ処理
**理由**: セキュリティは横断的関心事でありエンティティに属さない

### 4.2 操作定義

#### 4.2.1 sanitizeTaskInput操作

```
操作名: sanitizeTaskInput
目的: タスク入力データのサニタイゼーション（BR-005）

シグネチャ:
sanitizeTaskInput(
  rawInput: string,
  sanitizationPolicy: SanitizationPolicy
): SanitizedInput

処理内容:
1. HTMLタグの除去/エスケープ
2. スクリプトタグの無害化
3. 特殊文字のエスケープ
4. ホワイトリストベースのフィルタリング
5. 長さ制限の適用

ポリシー設定:
- STRICT: 厳格な制限（デフォルト）
- MODERATE: 一般的な制限
- LENIENT: 緩やかな制限

戻り値: SanitizedInput
- cleanInput: string（サニタイズ済み入力）
- modifications: Modification[]（変更履歴）
- riskLevel: SecurityRiskLevel（リスクレベル）
```

#### 4.2.2 checkSecurityConstraints操作

```
操作名: checkSecurityConstraints
目的: セキュリティ制約の確認

シグネチャ:
checkSecurityConstraints(
  input: string,
  context: TaskCreationContext
): SecurityCheckResult

チェック項目:
1. 悪意のあるペイロードの検出
2. 異常な文字パターンの識別
3. 大量データ攻撃の防止
4. 権限ベースの制約チェック

戻り値: SecurityCheckResult
- isPassed: boolean
- detectedThreats: SecurityThreat[]
- recommendedAction: SecurityAction
```

## 5. ドメインサービス間の連携

### 5.1 協調パターン

```
TaskCreationDomainService の実行フロー:

1. createNewTask() 呼び出し
2. TaskValidationDomainService.validateTaskCreation() → ValidationResult
3. ValidationResult.isValid が false の場合、例外発生
4. TaskSecurityDomainService.sanitizeTaskInput() → SanitizedInput
5. TaskSecurityDomainService.checkSecurityConstraints() → SecurityCheckResult
6. SecurityCheckResult.isPassed が false の場合、例外発生
7. TaskFactory.createTask() でエンティティ作成
8. TaskCreatedEvent 生成
9. TaskCreationResult 返却
```

### 5.2 依存関係

```
TaskCreationDomainService
    ├─→ TaskValidationDomainService
    ├─→ TaskSecurityDomainService
    └─→ TaskFactory

TaskValidationDomainService
    └─→ (外部依存なし)

TaskSecurityDomainService
    └─→ (セキュリティライブラリへの依存)
```

## 6. エラーハンドリング戦略

### 6.1 例外階層

```
TaskDomainException（基底例外）
├─→ TaskValidationException
│   ├─→ TaskNameValidationException
│   ├─→ TaskContextValidationException
│   └─→ TaskBusinessRuleViolationException
├─→ TaskSecurityException
│   ├─→ TaskInputSanitizationException
│   ├─→ TaskSecurityConstraintViolationException
│   └─→ TaskSecurityThreatDetectedException
└─→ TaskCreationException
    ├─→ TaskFactoryException
    └─→ TaskEventGenerationException
```

### 6.2 エラー処理方針

1. **バリデーションエラー**: 詳細情報を含む例外で即座に処理中断
2. **セキュリティエラー**: ログ記録後、安全な状態で処理中断
3. **作成エラー**: リトライ可能性を考慮した例外設計

## 7. テスト戦略

### 7.1 単体テスト

各ドメインサービスの独立テスト：
- 正常ケースの動作確認
- 境界値での動作確認
- 例外ケースの処理確認
- ビジネスルール違反時の動作確認

### 7.2 統合テスト

ドメインサービス間の連携テスト：
- サービス間のデータフロー確認
- エラー伝播の確認
- パフォーマンス要件の確認

## 8. 実装時の考慮事項

### 8.1 パフォーマンス

- バリデーション処理の効率化
- セキュリティチェックの最適化
- 不要な処理の回避

### 8.2 拡張性

- 新しいバリデーションルールの追加容易性
- セキュリティポリシーの変更対応
- 国際化対応の準備

### 8.3 保守性

- ビジネスルールの可視化
- ログ出力の標準化
- 設定の外部化

## 9. 他ユニットとの関連

### 9.1 インターフェース提供

TaskCreationDomainService は他ユニットに対して以下を提供：
- タスク作成API
- 作成結果の通知
- エラー情報の詳細

### 9.2 依存関係管理

- リポジトリインターフェースへの依存
- 外部サービスインターフェースへの依存
- 設定・ポリシー管理への依存

---

**次フェーズへの引き継ぎ**:
- 3つのドメインサービス設計完了
- ビジネスルール実装の詳細設計完了
- セキュリティ要件とバリデーション要件の具体化完了