"""
Excel sheet creation using xlsxwriter.
"""
from typing import List, Dict
from datetime import datetime
from loguru import logger

from backend.models.review import Review
from backend.models.analysis_result import AnalysisResult, OTAAnalysis, KeywordResult
from backend.services.excel.charts import ChartGenerator
from backend.utils.exceptions import SheetCreationError


class SheetCreator:
    """Creator for Excel sheets."""

    @staticmethod
    def create_summary_sheet(
        workbook,
        result: AnalysisResult,
        hotel_name: str
    ):
        """
        Create summary sheet with overall statistics and charts.

        Args:
            workbook: XlsxWriter workbook object
            result: Analysis result
            hotel_name: Hotel name

        Returns:
            Worksheet object
        """
        try:
            worksheet = workbook.add_worksheet("サマリー")

            # Define formats
            title_format = workbook.add_format({
                "bold": True,
                "font_size": 16,
                "align": "left",
                "bg_color": "#4472C4",
                "font_color": "white"
            })
            header_format = workbook.add_format({
                "bold": True,
                "font_size": 12,
                "align": "left",
                "bg_color": "#D9E1F2"
            })
            label_format = workbook.add_format({
                "bold": True,
                "align": "right"
            })
            value_format = workbook.add_format({
                "align": "left"
            })

            # Set column widths
            worksheet.set_column("A:A", 20)
            worksheet.set_column("B:B", 30)

            row = 0

            # Title
            worksheet.merge_range(row, 0, row, 1, f"ホテル口コミ分析レポート: {hotel_name}", title_format)
            row += 2

            # Analysis info
            worksheet.write(row, 0, "分析日時:", label_format)
            worksheet.write(row, 1, result.analyzed_at.strftime("%Y-%m-%d %H:%M:%S"), value_format)
            row += 1

            worksheet.write(row, 0, "分析期間:", label_format)
            worksheet.write(row, 1, f"{result.start_date.strftime('%Y-%m-%d')} 〜 {result.end_date.strftime('%Y-%m-%d')}", value_format)
            row += 2

            # Overall statistics header
            worksheet.write(row, 0, "全体統計", header_format)
            row += 1

            worksheet.write(row, 0, "総レビュー数:", label_format)
            worksheet.write(row, 1, result.total_reviews, value_format)
            row += 1

            worksheet.write(row, 0, "平均評価:", label_format)
            worksheet.write(row, 1, f"{result.average_rating:.2f} / 5.0", value_format)
            row += 1

            worksheet.write(row, 0, "平均感情スコア:", label_format)
            worksheet.write(row, 1, f"{result.average_sentiment:.3f} (-1〜1)", value_format)
            row += 2

            # Sentiment distribution
            worksheet.write(row, 0, "感情分布", header_format)
            row += 1

            for sentiment, count in result.sentiment_distribution.items():
                label = {"positive": "ポジティブ", "neutral": "ニュートラル", "negative": "ネガティブ"}.get(sentiment, sentiment)
                worksheet.write(row, 0, f"{label}:", label_format)
                worksheet.write(row, 1, count, value_format)
                row += 1

            row += 1

            # OTA breakdown
            worksheet.write(row, 0, "OTA別内訳", header_format)
            row += 1

            for ota in result.ota_analyses:
                worksheet.write(row, 0, f"{ota.ota_name.upper()}:", label_format)
                worksheet.write(row, 1, f"{ota.total_reviews}件 (平均評価: {ota.average_rating:.2f})", value_format)
                row += 1

            # Add charts
            ChartGenerator.create_sentiment_pie_chart(
                workbook, worksheet,
                result.sentiment_distribution,
                "D2",
                "感情分布"
            )

            ChartGenerator.create_rating_distribution_chart(
                workbook, worksheet,
                result.rating_distribution,
                "D20",
                "評価分布"
            )

            logger.info("✅ Summary sheet created")
            return worksheet

        except Exception as e:
            logger.error(f"Failed to create summary sheet: {str(e)}")
            raise SheetCreationError(f"Summary sheet creation failed: {str(e)}")

    @staticmethod
    def create_reviews_sheet(
        workbook,
        reviews: List[Review]
    ):
        """
        Create reviews list sheet with all review data.

        Args:
            workbook: XlsxWriter workbook object
            reviews: List of reviews

        Returns:
            Worksheet object
        """
        try:
            worksheet = workbook.add_worksheet("口コミ一覧")

            # Define formats
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#4472C4",
                "font_color": "white",
                "border": 1
            })
            cell_format = workbook.add_format({
                "border": 1,
                "text_wrap": True,
                "valign": "top"
            })

            # Set column widths
            columns = {
                "A": ("OTA", 10),
                "B": ("レビュー日", 12),
                "C": ("評価", 8),
                "D": ("感情", 10),
                "E": ("感情スコア", 12),
                "F": ("タイトル", 20),
                "G": ("コメント", 60),
                "H": ("レビュアー", 15),
                "I": ("旅行タイプ", 12)
            }

            for col, (label, width) in columns.items():
                col_idx = ord(col) - ord("A")
                worksheet.set_column(col_idx, col_idx, width)
                worksheet.write(0, col_idx, label, header_format)

            # Write review data
            for row_idx, review in enumerate(reviews, start=1):
                worksheet.write(row_idx, 0, review.source.value.upper(), cell_format)
                worksheet.write(row_idx, 1, review.review_date.strftime("%Y-%m-%d"), cell_format)
                worksheet.write(row_idx, 2, review.rating, cell_format)

                sentiment_label = {
                    "positive": "ポジティブ",
                    "neutral": "ニュートラル",
                    "negative": "ネガティブ"
                }.get(review.sentiment, "")
                worksheet.write(row_idx, 3, sentiment_label, cell_format)

                sentiment_score = review.sentiment_score if review.sentiment_score is not None else ""
                worksheet.write(row_idx, 4, sentiment_score, cell_format)

                worksheet.write(row_idx, 5, review.title or "", cell_format)
                worksheet.write(row_idx, 6, review.comment, cell_format)
                worksheet.write(row_idx, 7, review.reviewer_name or "", cell_format)
                worksheet.write(row_idx, 8, review.trip_type or "", cell_format)

            # Freeze header row
            worksheet.freeze_panes(1, 0)

            # Add conditional formatting for sentiment score
            if len(reviews) > 0:
                worksheet.conditional_format(1, 4, len(reviews), 4, {
                    "type": "3_color_scale",
                    "min_color": "#FF0000",
                    "mid_color": "#FFFF00",
                    "max_color": "#00FF00"
                })

            logger.info(f"✅ Reviews sheet created with {len(reviews)} reviews")
            return worksheet

        except Exception as e:
            logger.error(f"Failed to create reviews sheet: {str(e)}")
            raise SheetCreationError(f"Reviews sheet creation failed: {str(e)}")

    @staticmethod
    def create_ota_sheet(
        workbook,
        ota_analysis: OTAAnalysis,
        reviews: List[Review]
    ):
        """
        Create OTA-specific analysis sheet.

        Args:
            workbook: XlsxWriter workbook object
            ota_analysis: OTA analysis result
            reviews: Reviews for this OTA

        Returns:
            Worksheet object
        """
        try:
            sheet_name = f"{ota_analysis.ota_name.upper()}分析"
            worksheet = workbook.add_worksheet(sheet_name)

            # Define formats
            title_format = workbook.add_format({
                "bold": True,
                "font_size": 14,
                "bg_color": "#4472C4",
                "font_color": "white"
            })
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#D9E1F2"
            })
            label_format = workbook.add_format({"bold": True})

            # Set column widths
            worksheet.set_column("A:A", 20)
            worksheet.set_column("B:B", 30)

            row = 0

            # Title
            worksheet.merge_range(row, 0, row, 1, f"{ota_analysis.ota_name.upper()} 分析", title_format)
            row += 2

            # Statistics
            worksheet.write(row, 0, "総レビュー数:", label_format)
            worksheet.write(row, 1, ota_analysis.total_reviews)
            row += 1

            worksheet.write(row, 0, "平均評価:", label_format)
            worksheet.write(row, 1, f"{ota_analysis.average_rating:.2f}")
            row += 1

            worksheet.write(row, 0, "平均感情スコア:", label_format)
            worksheet.write(row, 1, f"{ota_analysis.average_sentiment:.3f}")
            row += 2

            # Sentiment breakdown
            worksheet.write(row, 0, "感情内訳", header_format)
            row += 1

            worksheet.write(row, 0, "ポジティブ:", label_format)
            worksheet.write(row, 1, ota_analysis.positive_count)
            row += 1

            worksheet.write(row, 0, "ニュートラル:", label_format)
            worksheet.write(row, 1, ota_analysis.neutral_count)
            row += 1

            worksheet.write(row, 0, "ネガティブ:", label_format)
            worksheet.write(row, 1, ota_analysis.negative_count)
            row += 2

            # Top keywords
            worksheet.write(row, 0, "TOP キーワード", header_format)
            row += 1

            for i, keyword in enumerate(ota_analysis.top_keywords[:10], 1):
                worksheet.write(row, 0, f"{i}. {keyword.keyword}", label_format)
                worksheet.write(row, 1, f"{keyword.frequency}回")
                row += 1

            # Add charts
            sentiment_dist = {
                "positive": ota_analysis.positive_count,
                "neutral": ota_analysis.neutral_count,
                "negative": ota_analysis.negative_count
            }

            ChartGenerator.create_sentiment_pie_chart(
                workbook, worksheet,
                sentiment_dist,
                "D2",
                f"{ota_analysis.ota_name.upper()} 感情分布"
            )

            ChartGenerator.create_keyword_bar_chart(
                workbook, worksheet,
                ota_analysis.top_keywords,
                "D20",
                f"{ota_analysis.ota_name.upper()} TOP キーワード"
            )

            logger.info(f"✅ {sheet_name} created")
            return worksheet

        except Exception as e:
            logger.error(f"Failed to create OTA sheet: {str(e)}")
            raise SheetCreationError(f"OTA sheet creation failed: {str(e)}")

    @staticmethod
    def create_keywords_sheet(
        workbook,
        result: AnalysisResult
    ):
        """
        Create keywords analysis sheet.

        Args:
            workbook: XlsxWriter workbook object
            result: Analysis result

        Returns:
            Worksheet object
        """
        try:
            worksheet = workbook.add_worksheet("キーワード分析")

            # Define formats
            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#4472C4",
                "font_color": "white",
                "border": 1
            })
            cell_format = workbook.add_format({"border": 1})

            # Set column widths
            worksheet.set_column("A:A", 15)
            worksheet.set_column("B:B", 10)
            worksheet.set_column("C:C", 10)
            worksheet.set_column("D:D", 12)

            # Headers
            worksheet.write(0, 0, "キーワード", header_format)
            worksheet.write(0, 1, "出現回数", header_format)
            worksheet.write(0, 2, "スコア", header_format)
            worksheet.write(0, 3, "カテゴリ", header_format)

            # Write keyword data
            for row_idx, keyword in enumerate(result.top_keywords, start=1):
                worksheet.write(row_idx, 0, keyword.keyword, cell_format)
                worksheet.write(row_idx, 1, keyword.frequency, cell_format)
                worksheet.write(row_idx, 2, f"{keyword.score:.3f}", cell_format)
                worksheet.write(row_idx, 3, keyword.category or "", cell_format)

            # Freeze header
            worksheet.freeze_panes(1, 0)

            # Add chart
            ChartGenerator.create_keyword_bar_chart(
                workbook, worksheet,
                result.top_keywords,
                "F2",
                "TOP 10 キーワード"
            )

            logger.info("✅ Keywords sheet created")
            return worksheet

        except Exception as e:
            logger.error(f"Failed to create keywords sheet: {str(e)}")
            raise SheetCreationError(f"Keywords sheet creation failed: {str(e)}")
