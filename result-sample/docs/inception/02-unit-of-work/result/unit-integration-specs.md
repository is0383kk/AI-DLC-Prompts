# ユニット間連携仕様書

## 文書概要

**文書名**: ユニット間連携仕様書
**作成日**: 2025-10-22
**対象プロジェクト**: シンプルなタスク管理アプリ
**目的**: 4つの作業ユニット間の連携方法と統合仕様を定義

## 全体アーキテクチャ

### ユニット構成
```
┌─────────────────┐    TaskDataInterface    ┌─────────────────┐
│   ユニット1     │ ──────────────────────→ │   ユニット2     │
│ タスク作成機能  │                         │ タスク表示機能  │
└─────────────────┘                         └─────────────────┘
                                                      │ │
                              TaskSelectionInterface  │ │ TaskDeletionInterface
                                                      ↓ ↓
┌─────────────────┐                         ┌─────────────────┐
│   ユニット3     │                         │   ユニット4     │
│ タスク編集機能  │                         │ タスク削除機能  │
└─────────────────┘                         └─────────────────┘
         │                                           │
         │ TaskUpdateNotificationInterface           │ TaskDeletionNotificationInterface
         └─────────────────────────────────────────────┘
                               │
                               ↓
                    ┌─────────────────┐
                    │   ユニット2     │
                    │ タスク表示機能  │
                    │   (更新反映)    │
                    └─────────────────┘
```

### データフロー
1. **作成フロー**: ユニット1 → データ層 → ユニット2
2. **表示フロー**: データ層 → ユニット2 → UI
3. **編集フロー**: ユニット2 → ユニット3 → データ層 → ユニット2
4. **削除フロー**: ユニット2 → ユニット4 → データ層 → ユニット2

## インターフェース定義

### 1. TaskDataInterface（ユニット1 → ユニット2）

**概要**: タスク作成時のデータ転送インターフェース

**データ構造**:
```typescript
interface TaskData {
  taskId: string;          // 一意識別子（UUID推奨）
  taskName: string;        // タスク名（最大100文字）
  createdAt: Date;         // 作成日時（ISO 8601形式）
  status: 'incomplete' | 'complete';  // 初期値は'incomplete'
  updatedAt?: Date;        // 更新日時（作成時はnull）
}
```

**通信方法**: データ永続化層経由（LocalStorage/Database）
**トリガー**: 新規タスク作成完了時
**レスポンス**: 作成成功/失敗の通知

### 2. TaskSelectionInterface（ユニット2 → ユニット3）

**概要**: タスク編集モード開始時の選択情報転送

**データ構造**:
```typescript
interface TaskSelection {
  selectedTaskId: string;  // 選択されたタスクID
  editMode: boolean;       // 編集モード開始フラグ
  taskData: TaskData;      // 編集対象のタスクデータ
}
```

**通信方法**: 画面遷移・状態管理経由
**トリガー**: 編集ボタンクリック時
**レスポンス**: 編集画面の表示開始

### 3. TaskDeletionInterface（ユニット2 → ユニット4）

**概要**: タスク削除モード開始時の選択情報転送

**データ構造**:
```typescript
interface TaskDeletion {
  selectedTaskId: string;  // 選択されたタスクID
  deleteMode: boolean;     // 削除モード開始フラグ
  taskData: TaskData;      // 削除対象のタスクデータ
}
```

**通信方法**: 画面遷移・状態管理経由
**トリガー**: 削除ボタンクリック時
**レスポンス**: 削除確認ダイアログの表示

### 4. TaskUpdateNotificationInterface（ユニット3 → ユニット2）

**概要**: タスク編集完了時の更新通知

**データ構造**:
```typescript
interface TaskUpdateNotification {
  updatedTaskId: string;           // 更新されたタスクID
  updateType: 'content' | 'status'; // 更新種別
  updateResult: boolean;           // 更新成功/失敗
  updatedData?: TaskData;          // 更新後のタスクデータ
  errorMessage?: string;           // エラー時のメッセージ
}
```

**通信方法**: イベント通知・Observer パターン
**トリガー**: 編集保存完了時
**レスポンス**: タスク一覧の再表示

### 5. TaskDeletionNotificationInterface（ユニット4 → ユニット2）

**概要**: タスク削除完了時の削除通知

**データ構造**:
```typescript
interface TaskDeletionNotification {
  deletedTaskId: string;   // 削除されたタスクID
  deleteResult: boolean;   // 削除成功/失敗
  errorMessage?: string;   // エラー時のメッセージ
}
```

**通信方法**: イベント通知・Observer パターン
**トリガー**: 削除処理完了時
**レスポンス**: タスク一覧の再表示

## 状態管理仕様

### グローバル状態
```typescript
interface AppState {
  tasks: TaskData[];           // 全タスクリスト
  selectedTaskId?: string;     // 現在選択中のタスクID
  currentView: 'list' | 'edit' | 'delete'; // 現在の画面状態
  isLoading: boolean;          // 処理中フラグ
  error?: string;              // エラーメッセージ
}
```

### 状態遷移
1. **初期状態** → `{ tasks: [], currentView: 'list', isLoading: false }`
2. **タスク作成** → `isLoading: true` → 作成完了 → `tasks` 更新
3. **編集開始** → `currentView: 'edit'`, `selectedTaskId` 設定
4. **編集完了** → `currentView: 'list'`, `tasks` 更新, `selectedTaskId` クリア
5. **削除開始** → `currentView: 'delete'`, `selectedTaskId` 設定
6. **削除完了** → `currentView: 'list'`, `tasks` 更新, `selectedTaskId` クリア

## エラーハンドリング仕様

### エラー分類と対処
1. **通信エラー**: ネットワーク障害、API応答なし
2. **バリデーションエラー**: 入力データの不正
3. **競合エラー**: 同時編集・削除の競合
4. **システムエラー**: 予期しない内部エラー

### エラー処理フロー
```
エラー発生 → エラー分類 → ユーザー通知 → 復旧処理 → 状態復元
```

### 具体的な対処方法
- **通信エラー**: 再試行機能、オフライン対応
- **バリデーションエラー**: 入力フィールドへのエラー表示
- **競合エラー**: 最新データの再取得、ユーザー選択
- **システムエラー**: 適切なエラーメッセージ、開発者への通知

## 実装順序と統合ポイント

### フェーズ1: 基盤構築（ユニット1 + ユニット2）
**統合ポイント**:
- TaskDataInterface の実装・テスト
- データ永続化機能の実装
- 基本的なCRUD操作の動作確認

**統合テスト項目**:
- タスク作成 → 一覧表示の確認
- データ永続化の確認
- エラーハンドリングの確認

### フェーズ2: 編集機能追加（ユニット3）
**統合ポイント**:
- TaskSelectionInterface の実装・テスト
- TaskUpdateNotificationInterface の実装・テスト
- 編集フローの統合

**統合テスト項目**:
- タスク選択 → 編集 → 保存 → 表示更新の確認
- 編集キャンセル時の状態保持確認
- 同時編集時の競合処理確認

### フェーズ3: 削除機能追加（ユニット4）
**統合ポイント**:
- TaskDeletionInterface の実装・テスト
- TaskDeletionNotificationInterface の実装・テスト
- 削除フローの統合

**統合テスト項目**:
- タスク選択 → 削除確認 → 削除 → 表示更新の確認
- 削除キャンセル時の状態保持確認
- 最後のタスク削除時の空状態表示確認

## 技術的実装ガイドライン

### データ永続化方式
**推奨**: LocalStorage + JSON形式
**代替**: IndexedDB（大量データ対応時）

### 状態管理方式
**推奨**: React Context + useReducer または Vuex/Redux
**代替**: シンプルな状態管理ライブラリ

### 通信方式
**推奨**: イベントバス または カスタムフック
**代替**: Props drilling（小規模の場合）

### テスト戦略
1. **単体テスト**: 各ユニット内の機能テスト
2. **統合テスト**: ユニット間インターフェースのテスト
3. **E2Eテスト**: 全体フローの動作確認

## 運用・保守時の考慮事項

### パフォーマンス監視
- TaskDataInterface の応答時間監視
- 大量タスク時の表示性能監視
- メモリ使用量の監視

### 拡張性考慮
- 新機能追加時のインターフェース拡張方法
- 将来的なマルチユーザー対応への準備
- API化時の設計変更指針

### セキュリティ
- XSS対策（タスク名のサニタイゼーション）
- データ整合性の保証
- 不正操作の防止

## 開発チーム間の連携指針

### コミュニケーション
- インターフェース変更時の事前相談
- 統合テスト実施時の合同作業
- 問題発生時のエスカレーション手順

### 文書管理
- インターフェース仕様の変更履歴管理
- テスト結果の共有
- 実装上の課題・制約の記録

### リリース管理
- ユニット単位での機能確認
- 統合後の受け入れテスト
- 本番環境での動作検証

---

本仕様書は実装開始前の最終確認と、開発中の指針として活用してください。