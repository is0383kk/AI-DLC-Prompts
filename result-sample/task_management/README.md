# Task Management API - Unit1: タスク作成機能

タスク管理システムのタスク作成機能（Unit1）を提供する FastAPI アプリケーションです。

## 🚀 概要

### 実装済み機能

- **US-001**: 新しいタスクの追加
- **US-002**: タスクの基本情報入力
- **ビジネスルール**: BR-001 ～ BR-006 対応
- **受け入れ基準**: AC-001-01 ～ AC-002-03 対応

### アーキテクチャ

- **技術スタック**: FastAPI + Python 3.11+
- **設計手法**: ドメイン駆動設計（DDD）4 層アーキテクチャ
- **データ永続化**: インメモリリポジトリ

### プロジェクト構成

```
task_management/
├── main.py                           # FastAPI アプリケーション エントリーポイント
├── requirements.txt                  # Python依存関係
├── README.md                         # このファイル
├── domain/                          # ドメイン層
│   ├── entities/                    # エンティティ
│   │   └── task.py                  # タスクエンティティ（集約ルート）
│   ├── value_objects/               # 値オブジェクト
│   │   ├── task_id.py               # タスクID
│   │   ├── task_name.py             # タスク名
│   │   ├── task_status.py           # タスクステータス
│   │   └── datetime_value.py        # 日時値オブジェクト
│   ├── services/                    # ドメインサービス
│   │   ├── task_creation_domain_service.py     # タスク作成ドメインサービス
│   │   ├── task_validation_domain_service.py  # バリデーションサービス
│   │   └── task_security_domain_service.py    # セキュリティサービス
│   ├── factories/                   # ファクトリ
│   │   └── task_factory.py          # タスクファクトリ
│   ├── events/                      # ドメインイベント
│   │   ├── base_domain_event.py     # 基底ドメインイベント
│   │   └── task_created_event.py    # タスク作成イベント
│   └── exceptions/                  # ドメイン例外
│       └── domain_exceptions.py     # ドメイン例外定義
├── application/                     # アプリケーション層
│   ├── services/                    # アプリケーションサービス
│   │   └── task_creation_application_service.py  # タスク作成サービス
│   ├── commands/                    # コマンドオブジェクト
│   │   └── create_task_command.py   # タスク作成コマンド
│   └── responses/                   # レスポンスオブジェクト
│       ├── create_task_response.py  # 成功レスポンス
│       └── create_task_error_response.py  # エラーレスポンス
├── infrastructure/                  # インフラストラクチャ層
│   ├── repositories/                # リポジトリ実装
│   │   ├── task_repository.py       # リポジトリインターフェース
│   │   └── task_repository_impl.py  # インメモリリポジトリ実装
│   ├── events/                      # イベント発行
│   │   ├── event_publisher.py       # イベント発行インターフェース
│   │   └── event_publisher_impl.py  # イベント発行実装
│   ├── converters/                  # データ変換
│   │   └── task_data_converter.py   # タスクデータ変換
│   └── logging/                     # ログ出力
│       └── logger_impl.py           # ログ実装
└── presentation/                    # プレゼンテーション層
    ├── controllers/                 # コントローラー
    │   ├── task_creation_controller.py  # タスク作成API
    │   └── health_controller.py     # ヘルスチェックAPI
    └── dtos/                        # データ転送オブジェクト
        ├── create_task_request_dto.py   # リクエストDTO
        ├── task_response_dto.py      # タスクレスポンスDTO
        └── error_response_dto.py     # エラーレスポンスDTO
```

## 🛠️ 環境構築手順

### 前提条件

- Python 3.11 以上
- pip（Python パッケージマネージャー）

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd task_management

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. アプリケーションの起動

#### 方法 1: 直接実行

```bash
python main.py
```

#### 方法 2: uvicorn コマンド

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. 動作確認

アプリケーション起動後、以下の URL にアクセスして動作を確認：

- **API ドキュメント**: http://localhost:8000/docs
- **基本情報**: http://localhost:8000/
- **ヘルスチェック**: http://localhost:8000/health

## 📡 API エンドポイント

### タスク作成 API

#### `POST /api/tasks`

新しいタスクを作成します。

**リクエスト例**:

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "会議資料の準備",
    "user_id": "user123"
  }'
```

**レスポンス例（成功）**:

```json
{
  "task_id": "task_123e4567-e89b-12d3-a456-426614174000",
  "task_name": "会議資料の準備",
  "status": "未完了",
  "created_at": "2025-10-23T10:30:00Z",
  "message": "タスクが正常に作成されました"
}
```

**レスポンス例（エラー）**:

```json
{
  "error_code": "VALIDATION_ERROR",
  "error_message": "バリデーションに失敗しました",
  "details": [
    {
      "field": "task_name",
      "code": "REQUIRED",
      "message": "タスク名は必須です",
      "value": null
    }
  ],
  "timestamp": "2025-10-23T10:30:00Z",
  "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
}
```

### ヘルスチェック API

#### `GET /health`

基本的なヘルスチェック（後方互換性のため）

#### `GET /health/detailed`

詳細なヘルスチェック（アプリケーション・依存関係・システムリソース）

#### `GET /health/readiness`

稼働準備状態チェック（Kubernetes readiness probe 用）

#### `GET /health/liveness`

生存状態チェック（Kubernetes liveness probe 用）

**詳細ヘルスチェック例**:

```bash
curl -X GET "http://localhost:8000/health/detailed"
```

## 🔧 設定・カスタマイズ

### ログレベル設定

`main.py` の logging.basicConfig で設定を変更できます：

```python
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### CORS の設定

開発環境では全てのオリジンを許可していますが、本番環境では適切に制限してください：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 本番では具体的なドメインを指定
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🧪 テスト・動作確認

### 基本動作テスト

#### 1. アプリケーション起動テスト

```bash
python main.py
```

コンソールに起動メッセージが表示されることを確認。

#### 2. ヘルスチェックテスト

```bash
curl http://localhost:8000/health
```

#### 3. タスク作成テスト

```bash
# 正常ケース
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"task_name": "テストタスク", "user_id": "test_user"}'

# バリデーションエラーケース
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"task_name": "", "user_id": "test_user"}'
```

#### 4. インメモリストレージ確認（デバッグ用）

```bash
curl http://localhost:8000/debug/storage
```

## 📊 監視・メトリクス

### システムメトリクス

`GET /metrics` エンドポイントで基本的なメトリクスを取得できます：

```bash
curl http://localhost:8000/metrics
```

### 詳細システム情報

`GET /health/detailed` で以下の情報を監視できます：

- CPU 使用率
- メモリ使用率
- ディスク使用率
- アプリケーション状態
- 依存関係状態

## 🔒 セキュリティ

### 実装済みセキュリティ対策

- **入力サニタイゼーション**: bleach ライブラリによる XSS 対策
- **入力バリデーション**: Pydantic による型安全性
- **構造化ログ**: 監査証跡の記録
- **エラーハンドリング**: 適切なエラーメッセージ

### 追加推奨事項（本番環境）

- HTTPS の使用
- レート制限の実装
- 認証・認可の実装
- セキュリティヘッダーの追加

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. 依存関係のインストールエラー

```bash
# Python バージョン確認
python --version

# pip アップグレード
python -m pip install --upgrade pip

# 再インストール
pip install -r requirements.txt
```

#### 2. ポート 8000 が使用中

```bash
# 他のプロセスがポートを使用している場合
netstat -ano | findstr :8000

# 別のポートで起動
uvicorn main:app --host 127.0.0.1 --port 8001
```

#### 3. インポートエラー

```bash
# Python パス確認
python -c "import sys; print(sys.path)"

# モジュール確認
python -c "from main import app; print('Success')"
```

#### 4. メモリ不足（大量データ処理時）

インメモリリポジトリを使用しているため、大量のタスクを作成するとメモリを消費します。
開発・テスト用途のため、本番環境では適切なデータベースを使用してください。

## 📝 ログファイル

ログは標準出力に出力されます。ファイルに出力したい場合：

```bash
# ログをファイルに保存
python main.py > task_management.log 2>&1

# リアルタイムでログを確認
tail -f task_management.log
```

## 🎯 パフォーマンス

### 期待されるパフォーマンス

- **タスク作成レスポンス時間**: < 100ms
- **ヘルスチェックレスポンス時間**: < 50ms
- **メモリ使用量**: < 100MB（1000 タスク以下）

### パフォーマンス監視

詳細ヘルスチェック（`/health/detailed`）でシステムリソースを監視できます。

## 🤝 サポート・問い合わせ

### 開発チーム連絡先

- **チーム**: Task Management Team
- **Email**: task-management@example.com

### ドキュメント

- **API 仕様**: http://localhost:8000/docs（起動時）
- **OpenAPI 仕様**: http://localhost:8000/openapi.json

---

## 📄 ライセンス

MIT License

---

**最終更新日**: 2025-10-23
**バージョン**: 1.0.0
