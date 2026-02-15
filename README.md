# 🏨 Hotel Review Analyzer

ホテル口コミ分析システム - 複数OTAからの口コミを一元管理し、感情分析とキーワード抽出を行い、Excel形式でレポートを出力するWebアプリケーション

**🚀 Live Demo:** [Streamlit App](https://hotel-review-analyzer-cwzflxemngeggvgxm4juoe.streamlit.app/) | [API Backend](https://hotel-review-analyzer-hazel.vercel.app/)

## 📋 概要

このシステムは、楽天トラベル、じゃらん、Booking.comなどの主要OTA（オンライン旅行代理店）からホテルの口コミを収集し、以下の分析を提供します：

- **感情分析**: ポジティブ/ネガティブ/ニュートラルの分類と感情スコア算出
- **キーワード抽出**: 頻出キーワードと重要トピックの特定
- **統計分析**: 評価分布、OTA別比較、時系列トレンド
- **Excelレポート**: グラフ付きの詳細レポート自動生成

## 🎯 ビジネス価値

- ✅ 複数OTAの口コミを一元管理
- ✅ 感情分析による顧客満足度の定量的把握
- ✅ キーワード分析による改善点の特定
- ✅ Excelレポートで経営層への報告が容易

## 🛠️ 技術スタック

- **Backend**: FastAPI 0.115.0 + Python 3.10+
- **Frontend**: Streamlit 1.39.0
- **NLP**: Transformers (BERT), Janome
- **Excel**: XlsxWriter
- **Data Processing**: Pandas, NumPy
- **HTTP Client**: httpx

## 📁 ディレクトリ構造

```
hotel-review-analyzer/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── streamlit_app.py          # Streamlit UI
├── backend/
│   ├── main.py               # FastAPI app
│   ├── config.py             # Settings
│   ├── api/
│   │   ├── routes/           # API endpoints
│   │   └── schemas/          # Request/Response models
│   ├── services/
│   │   ├── ota/              # OTA clients
│   │   ├── analyzer/         # Analysis engines
│   │   └── excel/            # Excel generation
│   ├── models/               # Data models
│   └── utils/                # Utilities
├── data/                     # Temp data (gitignored)
├── output/                   # Excel output (gitignored)
├── tests/                    # Unit tests
└── scripts/                  # Setup scripts
```

## 🚀 セットアップ

### 前提条件

- **Python 3.10 - 3.13 推奨** (Python 3.14は一部パッケージが未対応)
- pip

**注意**: Python 3.14は一部のパッケージ（pydantic-core、pillow等）がまだ完全にサポートしていないため、Python 3.12または3.13の使用を推奨します。

### インストール手順

1. **リポジトリのクローン**

```bash
cd /Users/momozaki/dev/hotel-review-analyzer
```

2. **仮想環境の作成と有効化**

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

3. **依存関係のインストール**

```bash
pip install -r requirements.txt
```

4. **環境変数の設定**

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要なAPI認証情報を設定してください。

5. **NLPモデルのダウンロード（Phase 3で実装予定）**

```bash
python scripts/download_models.py
```

## 💻 使用方法

### 1. バックエンドAPIの起動

```bash
uvicorn backend.main:app --reload --port 8000
```

APIドキュメント: http://localhost:8000/docs

### 2. Streamlit UIの起動（別ターミナル）

```bash
streamlit run streamlit_app.py
```

アプリケーション: http://localhost:8501

### 3. ヘルスチェック

```bash
curl http://localhost:8000/health
```

## 📊 機能一覧

### Phase 1: 基盤構築 ✅ 完了

- [x] プロジェクト構造
- [x] FastAPI基本構造
- [x] Streamlit UI基本構造
- [x] ヘルスチェックエンドポイント
- [x] ロギング設定

### Phase 2: OTA連携 ✅ 完了

- [x] OTA抽象基底クラス
- [x] データモデル（Review, ReviewStats）
- [x] 楽天トラベルクライアント（モック実装）
- [x] じゃらんクライアント（モック実装）
- [x] Booking.comクライアント（モック実装）
- [x] 非同期並列取得
- [x] 口コミ取得APIエンドポイント

### Phase 3: 分析機能 ✅ 完了

- [x] 感情分析エンジン（キーワードベースモック）
- [x] キーワード抽出エンジン（形態素解析モック）
- [x] 分析APIエンドポイント
- [x] OTA別分析
- [x] ポジティブ/ネガティブキーワード抽出

### Phase 4: Excel生成 ✅ 完了

- [x] サマリーシート生成
- [x] 口コミ一覧シート生成
- [x] キーワード分析シート生成
- [x] OTA別分析シート生成（複数）
- [x] グラフ生成（評価分布、感情分布、キーワードランキング、OTA比較）
- [x] 条件付き書式（感情スコア）
- [x] ExcelエクスポートAPIエンドポイント

### Phase 5: UI統合 ✅ 完了

- [x] FastAPI連携（口コミ取得、分析、エクスポート）
- [x] ステップバイステップUI（3段階）
- [x] プログレスバー・スピナー
- [x] 結果プレビュー（4つのタブ）
- [x] 分析サマリー表示
- [x] Excelダウンロード機能

## 🧪 テスト

```bash
# 全テスト実行
pytest tests/

# カバレッジ付き
pytest --cov=backend tests/
```

## 📝 API仕様

### ヘルスチェック

```http
GET /health
```

**レスポンス:**
```json
{
  "status": "healthy",
  "app_name": "Hotel Review Analyzer",
  "version": "1.0.0",
  "timestamp": "2025-01-15T12:00:00"
}
```

## 🔧 環境変数

主要な環境変数（`.env.example`参照）:

```env
# FastAPI Settings
DEBUG=True
APP_NAME=Hotel Review Analyzer
BACKEND_PORT=8000

# OTA API Credentials
RAKUTEN_APP_ID=your_app_id
BOOKING_USERNAME=your_username
BOOKING_PASSWORD=your_password

# NLP Settings
SENTIMENT_MODEL=daigo/bert-base-japanese-sentiment
BATCH_SIZE=32

# Logging
LOG_LEVEL=INFO
```

## 🐛 トラブルシューティング

### バックエンドに接続できない

1. FastAPIが起動しているか確認
2. ポート8000が使用可能か確認
3. `.env`ファイルが正しく設定されているか確認

### NLPモデルのダウンロードに失敗

1. インターネット接続を確認
2. Hugging Faceのアクセストークンが必要な場合は設定
3. ディスク容量を確認（モデルは数百MB必要）

## 📦 開発

### 新機能の追加

1. `backend/services/`に新しいサービスを追加
2. `backend/api/routes/`に新しいエンドポイントを追加
3. `streamlit_app.py`にUI要素を追加
4. テストを追加

### コードスタイル

- PEP 8準拠
- Type hintsを使用
- Docstringsを記述

## 🗺️ ロードマップ

- **v1.0**: Phase 1-5の完全実装
- **v1.1**: 多言語対応（英語口コミ）
- **v1.2**: トピックモデリング（LDA）
- **v1.3**: 競合比較機能
- **v2.0**: Plotly Dashダッシュボード

## 📄 ライセンス

MIT License

## 👥 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📞 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

**開発状況**: **全Phase完了！ ✅🎉**

Phase 1-5 の全機能が実装されました。モックデータを使用した完全なE2Eフローが動作します。

**次のステップ**:
- Python 3.12環境で依存関係をインストール
- FastAPIとStreamlitを起動してテスト
- 実際のOTA APIまたはスクレイピングロジックを実装（本番化時）

**最終更新**: 2025-02-12
