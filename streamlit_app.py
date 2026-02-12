"""
Streamlit UI for Hotel Review Analyzer - Complete Implementation.
"""
import streamlit as st
import httpx
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import time
import os

# Page configuration
st.set_page_config(
    page_title="Hotel Review Analyzer",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
# Use environment variable for production, fallback to localhost for development
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def check_backend_health() -> bool:
    """Check if backend API is running."""
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def fetch_reviews(hotel_name: str, ota_sources: list, start_date, end_date, limit: int):
    """Fetch reviews from backend API."""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/reviews/fetch",
            json={
                "hotel_name": hotel_name,
                "ota_sources": ota_sources,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit_per_ota": limit
            },
            timeout=180.0  # 3 minutes
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"❌ エラー: {str(e)}")
        return None


def analyze_reviews(include_keywords=True, include_sentiment=True, keyword_limit=30):
    """Analyze reviews using backend API."""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/reviews/analyze",
            json={
                "include_keywords": include_keywords,
                "include_sentiment": include_sentiment,
                "keyword_limit": keyword_limit
            },
            timeout=180.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"❌ 分析エラー: {str(e)}")
        return None


def export_to_excel(hotel_name: str, include_charts=True, include_raw_data=True):
    """Export analysis to Excel."""
    try:
        response = httpx.post(
            f"{BACKEND_URL}/api/reviews/export",
            json={
                "hotel_name": hotel_name,
                "include_charts": include_charts,
                "include_raw_data": include_raw_data
            },
            timeout=180.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        st.error(f"❌ エクスポートエラー: {str(e)}")
        return None


def main():
    """Main application."""

    # Header
    st.title("🏨 ホテル口コミ分析システム")
    st.markdown("複数OTAから口コミを収集し、感情分析・キーワード抽出を行います")
    st.markdown("---")

    # Check backend status
    if not check_backend_health():
        st.error("⚠️ バックエンドAPIに接続できません")
        st.code("uvicorn backend.main:app --reload --port 8000", language="bash")
        st.stop()

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ 設定")

        st.subheader("API認証情報")
        st.caption("※APIキーなしでもデモデータで動作確認できます")

        with st.expander("楽天トラベル", expanded=False):
            rakuten_app_id = st.text_input(
                "Application ID",
                type="password",
                help="楽天トラベルのApplication ID"
            )

        with st.expander("じゃらん", expanded=False):
            jalan_api_key = st.text_input(
                "API Key",
                type="password",
                help="じゃらんのAPI Key"
            )

        with st.expander("Booking.com", expanded=False):
            booking_username = st.text_input("Username")
            booking_password = st.text_input("Password", type="password")

        st.markdown("---")
        st.success("✅ バックエンド接続: 正常")

    # Initialize session state
    if "fetch_response" not in st.session_state:
        st.session_state.fetch_response = None
    if "analysis_response" not in st.session_state:
        st.session_state.analysis_response = None
    if "excel_path" not in st.session_state:
        st.session_state.excel_path = None

    # Main area - Tabs
    main_tab, results_tab = st.tabs(["🔍 分析実行", "📊 結果表示"])

    with main_tab:
        st.subheader("📊 口コミ分析設定")

        # OTA Selection
        st.write("**OTA選択**")
        col_ota1, col_ota2, col_ota3 = st.columns(3)

        with col_ota1:
            use_rakuten = st.checkbox("楽天トラベル", value=True)
        with col_ota2:
            use_jalan = st.checkbox("じゃらん", value=True)
        with col_ota3:
            use_booking = st.checkbox("Booking.com", value=False)

        # Hotel search
        hotel_name = st.text_input(
            "ホテル名",
            value="東京ホテル",
            placeholder="例: 東京ホテル",
            help="分析対象のホテル名を入力してください"
        )

        # Date range
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input(
                "開始日",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        with col_date2:
            end_date = st.date_input(
                "終了日",
                value=datetime.now(),
                max_value=datetime.now()
            )

        # Review count
        review_limit = st.slider(
            "取得件数（OTA毎）",
            min_value=10,
            max_value=100,
            value=10,  # Reduced for testing
            step=10,
            help="各OTAから取得する口コミの最大件数"
        )

        st.markdown("---")

        # Step 1: Fetch Reviews
        st.subheader("ステップ 1: 口コミ取得")

        if st.button("🔍 口コミを取得", type="primary", use_container_width=True):
            if not hotel_name:
                st.warning("ホテル名を入力してください")
            else:
                ota_sources = []
                if use_rakuten:
                    ota_sources.append("rakuten")
                if use_jalan:
                    ota_sources.append("jalan")
                if use_booking:
                    ota_sources.append("booking")

                if not ota_sources:
                    st.warning("少なくとも1つのOTAを選択してください")
                else:
                    with st.spinner("口コミを取得中..."):
                        response = fetch_reviews(
                            hotel_name, ota_sources,
                            start_date, end_date, review_limit
                        )

                        if response and response.get("success"):
                            st.session_state.fetch_response = response
                            st.success(f"✅ {response['total_reviews']}件の口コミを取得しました")

                            # Show breakdown
                            col1, col2, col3 = st.columns(3)
                            for i, (ota, count) in enumerate(response['reviews_by_ota'].items()):
                                with [col1, col2, col3][i % 3]:
                                    st.metric(ota.upper(), f"{count}件")

        # Step 2: Analyze Reviews
        if st.session_state.fetch_response:
            st.markdown("---")
            st.subheader("ステップ 2: 感情分析・キーワード抽出")

            col_settings1, col_settings2 = st.columns(2)
            with col_settings1:
                include_sentiment = st.checkbox("感情分析を実行", value=True)
            with col_settings2:
                include_keywords = st.checkbox("キーワード抽出を実行", value=True)

            keyword_limit = st.slider("抽出するキーワード数", 10, 50, 30)

            if st.button("📈 分析を実行", type="primary", use_container_width=True):
                with st.spinner("分析中..."):
                    time.sleep(1)  # Brief pause for UX
                    response = analyze_reviews(
                        include_keywords, include_sentiment, keyword_limit
                    )

                    if response and response.get("success"):
                        st.session_state.analysis_response = response
                        st.success("✅ 分析が完了しました")
                        st.balloons()

        # Step 3: Export to Excel
        if st.session_state.analysis_response:
            st.markdown("---")
            st.subheader("ステップ 3: Excelエクスポート")

            col_export1, col_export2 = st.columns(2)
            with col_export1:
                include_charts = st.checkbox("グラフを含める", value=True)
            with col_export2:
                include_raw_data = st.checkbox("生データを含める", value=True)

            if st.button("📥 Excelを生成", type="primary", use_container_width=True):
                with st.spinner("Excelを生成中..."):
                    response = export_to_excel(
                        hotel_name, include_charts, include_raw_data
                    )

                    if response and response.get("success"):
                        st.session_state.excel_path = response['file_path']
                        st.success(f"✅ Excel生成完了!")
                        st.info(f"ファイルサイズ: {response['file_size'] / 1024:.1f}KB")
                        st.info(f"生成時間: {response['export_time']:.2f}秒")

            # Download button (if Excel was generated)
            if "excel_path" in st.session_state and st.session_state.excel_path:
                import os
                excel_path = st.session_state.excel_path

                if os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        excel_data = f.read()

                    st.download_button(
                        label="💾 Excelファイルをダウンロード",
                        data=excel_data,
                        file_name=os.path.basename(excel_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

                    # Preview Excel content
                    st.markdown("---")
                    st.subheader("📄 Excel内容プレビュー")

                    if excel_path.endswith('.xlsx'):
                        try:
                            excel_file = pd.ExcelFile(excel_path)

                            st.write(f"**シート数**: {len(excel_file.sheet_names)}")

                            # Show preview of each sheet
                            for sheet_name in excel_file.sheet_names:
                                with st.expander(f"📊 {sheet_name}", expanded=(sheet_name == "サマリー")):
                                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                                    st.dataframe(df, use_container_width=True)
                                    st.caption(f"行数: {len(df)}, 列数: {len(df.columns)}")
                        except Exception as e:
                            st.error(f"プレビュー表示エラー: {str(e)}")
                    else:
                        # Text file preview
                        with open(excel_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        st.text_area("ファイル内容", content, height=300)

    # Results Tab
    with results_tab:
        if st.session_state.analysis_response:
            result = st.session_state.analysis_response["analysis_result"]

            # Summary
            st.subheader("📊 分析サマリー")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("総レビュー数", result["total_reviews"])
            with col2:
                st.metric("平均評価", f"{result['average_rating']:.2f}")
            with col3:
                st.metric("平均感情スコア", f"{result['average_sentiment']:.3f}")
            with col4:
                st.metric("処理時間", f"{result['processing_time']:.2f}秒")

            st.markdown("---")

            # Tabs for detailed results
            detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs([
                "😊 感情分析",
                "🔑 キーワード",
                "📝 口コミ一覧",
                "🏢 OTA別分析"
            ])

            with detail_tab1:
                st.subheader("感情分布")

                # Sentiment distribution
                sent_dist = result["sentiment_distribution"]
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "ポジティブ",
                        sent_dist.get("positive", 0),
                        help="ポジティブな口コミの数"
                    )
                with col2:
                    st.metric(
                        "ニュートラル",
                        sent_dist.get("neutral", 0),
                        help="ニュートラルな口コミの数"
                    )
                with col3:
                    st.metric(
                        "ネガティブ",
                        sent_dist.get("negative", 0),
                        help="ネガティブな口コミの数"
                    )

                # Rating distribution
                st.subheader("評価分布")
                rating_df = pd.DataFrame({
                    "評価": list(result["rating_distribution"].keys()),
                    "件数": list(result["rating_distribution"].values())
                })
                st.bar_chart(rating_df.set_index("評価"))

            with detail_tab2:
                st.subheader("TOP キーワード")

                keywords = result.get("top_keywords", [])
                if keywords:
                    # Create DataFrame
                    kw_df = pd.DataFrame(keywords)
                    st.dataframe(
                        kw_df[["keyword", "frequency", "score", "category"]],
                        use_container_width=True,
                        hide_index=True
                    )

                    # Bar chart
                    st.bar_chart(
                        kw_df.set_index("keyword")["frequency"].head(10)
                    )
                else:
                    st.info("キーワードが抽出されていません")

                # Positive/Negative keywords
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("ポジティブキーワード")
                    pos_kw = result.get("positive_keywords", [])
                    if pos_kw:
                        for kw in pos_kw[:5]:
                            st.write(f"✅ {kw['keyword']} ({kw['frequency']}回)")
                    else:
                        st.info("データなし")

                with col2:
                    st.subheader("ネガティブキーワード")
                    neg_kw = result.get("negative_keywords", [])
                    if neg_kw:
                        for kw in neg_kw[:5]:
                            st.write(f"❌ {kw['keyword']} ({kw['frequency']}回)")
                    else:
                        st.info("データなし")

            with detail_tab3:
                if st.session_state.fetch_response:
                    reviews = st.session_state.fetch_response.get("reviews", [])

                    if reviews:
                        # Convert to DataFrame
                        df_data = []
                        for review in reviews:
                            df_data.append({
                                "OTA": review["source"].upper(),
                                "日付": review["review_date"][:10],
                                "評価": review["rating"],
                                "感情": review.get("sentiment", ""),
                                "スコア": review.get("sentiment_score", ""),
                                "コメント": review["comment"][:100] + "..."
                            })

                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        st.caption(f"全{len(reviews)}件のレビュー")
                    else:
                        st.info("口コミデータがありません")

            with detail_tab4:
                st.subheader("OTA別分析")

                ota_analyses = result.get("ota_analyses", [])
                if ota_analyses:
                    for ota in ota_analyses:
                        with st.expander(f"{ota['ota_name'].upper()} - {ota['total_reviews']}件", expanded=True):
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("平均評価", f"{ota['average_rating']:.2f}")
                            with col2:
                                st.metric("平均感情", f"{ota['average_sentiment']:.3f}")
                            with col3:
                                st.metric("ポジティブ率",
                                          f"{ota['positive_count'] / ota['total_reviews'] * 100:.1f}%")

                            # Top keywords for this OTA
                            if ota.get("top_keywords"):
                                st.write("**TOPキーワード:**")
                                kw_text = ", ".join([kw["keyword"] for kw in ota["top_keywords"][:5]])
                                st.write(kw_text)
                else:
                    st.info("OTA別分析データがありません")

        else:
            st.info("👈 左側のタブから分析を実行してください")

    # Footer
    st.markdown("---")
    st.caption("Hotel Review Analyzer v1.0.0 | Powered by FastAPI + Streamlit + Transformers")


if __name__ == "__main__":
    main()
