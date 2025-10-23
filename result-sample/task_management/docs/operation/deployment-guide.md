# Task Management API - 運用・デプロイメントガイド

**対象システム**: Task Management API - Unit1: タスク作成機能
**対象者**: 運用担当者、システム管理者
**最終更新**: 2025-10-23

## 📋 概要

本ドキュメントは、Task Management APIの運用・デプロイメントに関する手順とガイドラインを提供します。

## 🚀 デプロイメント手順

### ローカル環境でのデプロイメント

#### 前提条件
- Python 3.11 以上
- 8GB 以上のRAM推奨
- 1GB 以上の空きディスク容量

#### 手順

1. **環境準備**
   ```bash
   # プロジェクトディレクトリに移動
   cd task_management

   # 仮想環境作成（推奨）
   python -m venv venv

   # 仮想環境有効化
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **依存関係インストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **動作確認**
   ```bash
   # インポートテスト
   python -c "from main import app; print('Import successful')"

   # 基本動作テスト
   python -c "
   import asyncio
   from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
   repo = TaskRepositoryImpl()
   print('Repository initialization successful')
   "
   ```

4. **アプリケーション起動**
   ```bash
   # 開発モード（推奨）
   python main.py

   # または本番モード
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **起動確認**
   ```bash
   curl http://localhost:8000/health
   ```

### 本番環境への対応（将来拡張用）

#### 推奨構成
- **リバースプロキシ**: Nginx
- **プロセス管理**: Supervisor または systemd
- **ログ管理**: rsyslog + logrotate
- **監視**: Prometheus + Grafana

#### セキュリティ設定
```python
# main.py のCORS設定を本番用に変更
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # 具体的なドメインを指定
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

## 🔧 運用手順

### 日常運用チェック

#### 1. ヘルスチェック（推奨: 1日1回）
```bash
# 基本ヘルスチェック
curl http://localhost:8000/health

# 詳細ヘルスチェック
curl http://localhost:8000/health/detailed
```

**正常応答例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-23T10:30:00Z",
  "checks": {
    "application": {
      "status": "healthy",
      "uptime_seconds": 3600
    },
    "system_resources": {
      "status": "healthy",
      "cpu": {"usage_percent": 15.2, "status": "normal"},
      "memory": {"usage_percent": 45.8, "status": "normal"}
    }
  }
}
```

#### 2. システムリソース監視
```bash
# CPU・メモリ使用率確認
curl http://localhost:8000/health/detailed | jq '.checks.system_resources'

# アプリケーションメトリクス確認
curl http://localhost:8000/metrics
```

#### 3. ログ確認
```bash
# ログファイル確認（ファイル出力設定時）
tail -f task_management.log

# エラーログ検索
grep -i error task_management.log
```

### メンテナンス手順

#### アプリケーション再起動
```bash
# プロセス確認
ps aux | grep python | grep main.py

# 再起動
# Ctrl+C で停止後
python main.py

# または uvicorn使用時
pkill -f "uvicorn main:app"
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### データ確認・クリア（開発・テスト用）
```bash
# インメモリデータ確認
curl http://localhost:8000/debug/storage

# データクリア（アプリケーション再起動で自動的にクリア）
# インメモリのため、プロセス終了で全データが消失
```

### アップデート手順

#### 1. 依存関係更新
```bash
# requirements.txt 更新後
pip install -r requirements.txt --upgrade

# 特定パッケージ更新
pip install fastapi --upgrade
```

#### 2. アプリケーション更新
```bash
# ソースコード更新後
# 1. アプリケーション停止
# 2. 動作確認テスト実行
python -c "from main import app; print('Import test passed')"
# 3. アプリケーション再起動
python main.py
```

## 📊 監視・アラート

### 監視項目

#### システムメトリクス
- **CPU使用率**: 80%以下を維持
- **メモリ使用率**: 80%以下を維持
- **ディスク使用率**: 80%以下を維持
- **プロセス生存状態**: 常時稼働

#### アプリケーションメトリクス
- **レスポンス時間**: 100ms以下を目標
- **エラー率**: 1%以下を維持
- **作成タスク数**: 監視・記録
- **アップタイム**: 99%以上を目標

#### 監視スクリプト例
```bash
#!/bin/bash
# health_monitor.sh

ENDPOINT="http://localhost:8000/health/detailed"
THRESHOLD_CPU=80
THRESHOLD_MEMORY=80

response=$(curl -s $ENDPOINT)
status=$(echo $response | jq -r '.status')

if [ "$status" != "healthy" ]; then
    echo "ALERT: Application unhealthy - $response"
    # アラート送信処理
fi

cpu_usage=$(echo $response | jq -r '.checks.system_resources.cpu.usage_percent')
if (( $(echo "$cpu_usage > $THRESHOLD_CPU" | bc -l) )); then
    echo "ALERT: High CPU usage - $cpu_usage%"
fi
```

### ログ監視

#### 重要ログパターン
```bash
# エラーログ監視
grep -E "(ERROR|CRITICAL)" task_management.log

# セキュリティ関連ログ
grep -E "(SECURITY|VALIDATION|AUTHENTICATION)" task_management.log

# パフォーマンス関連ログ
grep -E "(SLOW|TIMEOUT|PERFORMANCE)" task_management.log
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. アプリケーション起動失敗

**症状**: `python main.py` でエラーが発生

**原因と対処**:
```bash
# 依存関係問題
pip install -r requirements.txt

# ポート競合問題
netstat -ano | findstr :8000
# 他のプロセスが使用中の場合は終了または別ポート使用

# Python パス問題
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. メモリ不足

**症状**: システムリソース不足エラー

**対処**:
```bash
# メモリ使用量確認
curl http://localhost:8000/health/detailed | jq '.checks.system_resources.memory'

# アプリケーション再起動（インメモリデータクリア）
# プロセス終了後再起動
```

#### 3. レスポンス遅延

**症状**: API応答が遅い

**対処**:
```bash
# システムリソース確認
curl http://localhost:8000/health/detailed

# CPU・メモリ使用率が高い場合は再起動
# ログでボトルネック特定
grep -i "slow\|timeout" task_management.log
```

#### 4. ヘルスチェック失敗

**症状**: `/health/detailed` が503エラー

**対処**:
```bash
# 基本ヘルスチェック確認
curl http://localhost:8000/health

# アプリケーションログ確認
tail -n 100 task_management.log

# 依存関係確認
python -c "
from infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from infrastructure.events.event_publisher_impl import EventPublisherImpl
print('Dependencies OK')
"
```

### エラーログ分析

#### ログレベル別対応

**CRITICAL/ERROR**:
- 即座に対応が必要
- アプリケーション停止の可能性
- システム管理者への即座の通知

**WARNING**:
- 監視が必要
- パフォーマンス低下の可能性
- 定期的な確認

**INFO**:
- 正常な動作ログ
- 統計・監査用途
- 定期的なレビュー

## 📈 パフォーマンス最適化

### 推奨設定

#### Python設定
```bash
# 本番環境では最適化フラグ使用
python -O main.py

# またはuvicorn設定
uvicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker
```

#### システム設定
```bash
# ファイルディスクリプタ制限確認・増加
ulimit -n
ulimit -n 65536

# プロセス制限確認
ulimit -u
```

### パフォーマンス測定
```bash
# Apache Bench を使用した負荷テスト
ab -n 1000 -c 10 http://localhost:8000/health

# curl を使用したレスポンス時間測定
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

curl-format.txt:
```
time_namelookup:  %{time_namelookup}\n
time_connect:     %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer: %{time_pretransfer}\n
time_redirect:    %{time_redirect}\n
time_starttransfer: %{time_starttransfer}\n
time_total:       %{time_total}\n
```

## 🔒 セキュリティ

### セキュリティチェックリスト

#### 運用時
- [ ] HTTPS使用（本番環境）
- [ ] CORS設定の適切な制限
- [ ] ログファイルのアクセス制限
- [ ] 定期的なセキュリティログ確認
- [ ] 依存関係の脆弱性チェック

#### 監視
```bash
# セキュリティ関連ログ確認
grep -E "(SECURITY|VALIDATION|ATTACK)" task_management.log

# 異常なアクセスパターン検出
grep -E "429|403|401" task_management.log
```

## 📞 エスカレーション

### 緊急時連絡先

**レベル1**: 運用チーム
- **対象**: 軽微な問題、定期メンテナンス
- **連絡先**: operation-team@example.com

**レベル2**: 開発チーム
- **対象**: アプリケーションエラー、機能問題
- **連絡先**: task-management@example.com

**レベル3**: システム管理者
- **対象**: システム障害、セキュリティインシデント
- **連絡先**: sysadmin@example.com

### エスカレーション基準

**即座にレベル3エスカレーション**:
- アプリケーション完全停止
- セキュリティ侵害の疑い
- データ破損・消失

**レベル2エスカレーション**:
- エラー率 > 5%
- レスポンス時間 > 1秒
- ヘルスチェック連続失敗

**レベル1対応**:
- CPU/メモリ使用率 > 80%
- ログファイル増大
- 軽微な設定変更

---

**最終更新**: 2025-10-23
**文書バージョン**: 1.0.0