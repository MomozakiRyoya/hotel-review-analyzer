# セキュリティ設定ガイド

## 概要

このプロジェクトでは、OTA（Booking.com、Expedia、Agoda）のAPIキーを環境変数で管理します。**APIキーは絶対にGitにコミットしないでください。**

## ローカル開発環境

### 1. 環境変数ファイルの作成

```bash
# .env.example をコピーして .env を作成
cp .env.example .env
```

### 2. APIキーの設定

`.env` ファイルを編集して、実際の認証情報を入力：

```bash
# Booking.com
BOOKING_USERNAME=actual_username
BOOKING_PASSWORD=actual_password
BOOKING_ENABLED=true

# Expedia
EXPEDIA_API_KEY=actual_api_key
EXPEDIA_API_SECRET=actual_api_secret
EXPEDIA_ENABLED=true

# Agoda
AGODA_API_KEY=actual_api_key
AGODA_PARTNER_ID=actual_partner_id
AGODA_ENABLED=true
```

### 3. .env ファイルの保護

```bash
# .env ファイルが .gitignore に含まれていることを確認
cat .gitignore | grep "^\.env$"

# .env ファイルのパーミッションを制限（推奨）
chmod 600 .env
```

## Vercel本番環境

### 環境変数の設定手順

1. **Vercelダッシュボードにアクセス**
   - https://vercel.com/
   - プロジェクト: `hotel-review-analyzer`

2. **環境変数ページを開く**
   - `Settings` → `Environment Variables`

3. **各環境変数を追加**

   | Variable Name | Value | Environment |
   |--------------|-------|-------------|
   | `BOOKING_USERNAME` | 実際の値 | Production, Preview |
   | `BOOKING_PASSWORD` | 実際の値 | Production, Preview |
   | `BOOKING_ENABLED` | `true` | Production |
   | `EXPEDIA_API_KEY` | 実際の値 | Production, Preview |
   | `EXPEDIA_API_SECRET` | 実際の値 | Production, Preview |
   | `EXPEDIA_ENABLED` | `true` | Production |
   | `AGODA_API_KEY` | 実際の値 | Production, Preview |
   | `AGODA_PARTNER_ID` | 実際の値 | Production, Preview |
   | `AGODA_ENABLED` | `true` | Production |

4. **再デプロイ**
   - 環境変数を追加/変更後、自動的に再デプロイされます

## APIキーの取得方法

### Booking.com
1. [Booking.com Developer Portal](https://developers.booking.com/) にアクセス
2. アカウント登録
3. Guest Review API へのアクセス申請
4. 承認後、認証情報を取得

### Expedia
1. [Expedia Group Developer Hub](https://developers.expediagroup.com/) にアクセス
2. パートナー登録
3. API クライアントを作成
4. Client ID と Client Secret を取得

### Agoda
1. [Agoda Partner Portal](https://partners.agoda.com/) にアクセス
2. アフィリエイト/パートナープログラムに申請
3. 承認後、Developer Portal でAPI Key を取得

## セキュリティチェックリスト

- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] `.env` ファイルをGitにコミットしていない
- [ ] Vercel環境変数が設定されている
- [ ] APIキーが公開リポジトリに含まれていない
- [ ] APIキーのパーミッションを最小限に設定（各OTAで）
- [ ] 定期的にAPIキーをローテーション

## トラブルシューティング

### エラー: "API credentials not configured"

**原因**: 環境変数が設定されていない

**解決策**:
```bash
# ローカル: .env ファイルを確認
cat .env

# Vercel: 環境変数を確認
vercel env ls
```

### エラー: "Authentication failed"

**原因**: APIキーが無効または期限切れ

**解決策**:
1. 各OTAのダッシュボードでAPIキーの状態を確認
2. 必要に応じて新しいキーを生成
3. 環境変数を更新

## 緊急時の対応

### APIキーが漏洩した場合

1. **即座に無効化**
   - 各OTAのダッシュボードで該当のキーを無効化

2. **新しいキーを生成**
   - 新しいAPIキーを発行

3. **環境変数を更新**
   ```bash
   # ローカル
   vim .env
   
   # Vercel
   vercel env add BOOKING_USERNAME
   ```

4. **影響範囲の調査**
   - アクセスログを確認
   - 不正利用の有無を確認

## 参考リンク

- [Vercel Environment Variables Documentation](https://vercel.com/docs/concepts/projects/environment-variables)
- [Booking.com Authentication](https://developers.booking.com/connectivity/docs/authentication)
- [Expedia API Setup](https://developers.expediagroup.com/analytics/resources/api-setup)
- [Agoda API Documentation](https://partners.agoda.com/DeveloperPortal/APIDoc)
