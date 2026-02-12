# デプロイガイド

このガイドでは、ホテル口コミ分析システムを公開する手順を説明します。

## アーキテクチャ

- **バックエンド (FastAPI)**: Vercelにデプロイ
- **フロントエンド (Streamlit)**: Streamlit Cloudにデプロイ

---

## ステップ1: GitHubにコードをプッシュ

### 1.1 Git初期化（まだの場合）

```bash
cd /Users/momozaki/dev/hotel-review-analyzer
git init
git add .
git commit -m "Initial commit: Hotel Review Analyzer"
```

### 1.2 GitHubリポジトリ作成

1. https://github.com/new にアクセス
2. リポジトリ名: `hotel-review-analyzer`
3. Private or Public を選択（推奨: Private）
4. 「Create repository」をクリック

### 1.3 リモートリポジトリに接続

```bash
git remote add origin https://github.com/YOUR_USERNAME/hotel-review-analyzer.git
git branch -M main
git push -u origin main
```

---

## ステップ2: バックエンドをVercelにデプロイ

### 2.1 Vercelアカウント作成

1. https://vercel.com にアクセス
2. 「Sign Up」をクリック
3. GitHubアカウントで登録

### 2.2 プロジェクトをインポート

1. Vercelダッシュボードで「Add New... → Project」
2. GitHubリポジトリから `hotel-review-analyzer` を選択
3. 「Import」をクリック

### 2.3 ビルド設定

**Framework Preset**: Other

**Build Command**:
```bash
pip install -r requirements-vercel.txt
```

**Output Directory**: (空白のまま)

**Install Command**: (デフォルトのまま)

### 2.4 環境変数を設定

「Environment Variables」セクションで以下を追加：

| Name | Value |
|------|-------|
| `RAKUTEN_APP_ID` | `1073657691050362412` |
| `VERCEL` | `1` |

### 2.5 デプロイ

1. 「Deploy」をクリック
2. 数分待つ
3. デプロイ完了後、URLが表示されます（例: `https://hotel-review-analyzer.vercel.app`）

**このURLをメモしてください！**

---

## ステップ3: フロントエンド（Streamlit）をStreamlit Cloudにデプロイ

### 3.1 Streamlit Cloudアカウント作成

1. https://streamlit.io/cloud にアクセス
2. 「Sign up」をクリック
3. GitHubアカウントで登録

### 3.2 Streamlit設定ファイル作成

プロジェクトルートに `.streamlit/config.toml` を作成済み（自動）

### 3.3 アプリをデプロイ

1. Streamlit Cloudダッシュボードで「New app」をクリック
2. 以下を入力：
   - **Repository**: `YOUR_USERNAME/hotel-review-analyzer`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`

3. 「Advanced settings」をクリック

4. **Environment variables**に以下を追加：

```
BACKEND_URL=https://YOUR-VERCEL-APP.vercel.app
```

（ステップ2.5でメモしたVercel URLを使用）

5. 「Deploy!」をクリック

### 3.4 デプロイ完了

数分後、StreamlitアプリのURLが表示されます：
```
https://YOUR-APP-NAME.streamlit.app
```

---

## ステップ4: バックエンドURLを設定

Streamlitアプリが正しくバックエンドに接続できるよう、`streamlit_app.py`を更新します。

### 4.1 streamlit_app.pyを編集

```python
# API Configuration
import os
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
```

この変更をコミット＆プッシュ：

```bash
git add streamlit_app.py
git commit -m "Update backend URL for production"
git push
```

Streamlit Cloudが自動的に再デプロイします。

---

## ステップ5: 動作確認

1. Streamlit CloudのURLにアクセス
2. ホテル名を入力（例: 「東京ステーションホテル」）
3. 「口コミを取得」をクリック
4. 本物の口コミが表示されることを確認

---

## トラブルシューティング

### エラー: "Backend API connection failed"

**原因**: Streamlitがバックエンドに接続できない

**解決策**:
1. Streamlit Cloudの環境変数 `BACKEND_URL` が正しく設定されているか確認
2. Vercelのデプロイが成功しているか確認
3. VercelのURLに直接アクセスして `/health` エンドポイントをテスト

### エラー: "Module not found"

**原因**: 依存パッケージがインストールされていない

**解決策**:
- Vercel: `requirements-vercel.txt` が正しいか確認
- Streamlit Cloud: `requirements.txt` が正しいか確認

### パフォーマンス問題

**Vercelの制限**:
- 実行時間: 10秒（Hobby plan）
- メモリ: 1024MB

大量の口コミを処理する場合、制限に達する可能性があります。
その場合、取得件数を減らすか、Pro planへのアップグレードを検討してください。

---

## コスト

### 無料枠

- **Vercel**: 月100GB帯域幅、無制限デプロイ
- **Streamlit Cloud**: 1アプリ無料（Private repos対応）

### 有料プラン（必要な場合）

- **Vercel Pro**: $20/月
- **Streamlit Cloud Team**: $250/月（複数アプリ）

通常の使用では無料枠で十分です。

---

## セキュリティ

### APIキーの管理

- ✅ 環境変数に保存（コードに直接書かない）
- ✅ GitHubリポジトリをPrivateに設定
- ✅ `.env`ファイルは`.gitignore`に含める

### 本番環境での注意事項

1. レート制限を設定（楽天APIの利用制限を守る）
2. エラーログを監視
3. 定期的にAPIキーをローテーション

---

## 更新方法

コードを変更した場合：

```bash
git add .
git commit -m "Update: 変更内容"
git push
```

- **Vercel**: 自動的に再デプロイ
- **Streamlit Cloud**: 自動的に再デプロイ

---

## サポート

問題が発生した場合：

1. Vercelログを確認: https://vercel.com/dashboard
2. Streamlit Cloudログを確認: https://streamlit.io/cloud
3. GitHubのIssueで報告

---

おめでとうございます！🎉
ホテル口コミ分析システムが公開されました！
