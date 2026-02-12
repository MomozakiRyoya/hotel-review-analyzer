"""
Excel chart generation using xlsxwriter.
"""
from typing import Dict, List, Optional
from loguru import logger

from backend.models.analysis_result import AnalysisResult, OTAAnalysis, KeywordResult
from backend.utils.exceptions import ChartCreationError


class ChartGenerator:
    """Generator for Excel charts."""

    @staticmethod
    def create_rating_distribution_chart(
        workbook,
        worksheet,
        rating_dist: Dict[str, int],
        chart_position: str = "A1",
        title: str = "評価分布"
    ):
        """
        Create rating distribution bar chart.

        Args:
            workbook: XlsxWriter workbook object
            worksheet: Worksheet object
            rating_dist: Rating distribution dictionary
            chart_position: Chart position (e.g., "A1")
            title: Chart title
        """
        try:
            chart = workbook.add_chart({"type": "column"})

            # Prepare data
            ratings = sorted(rating_dist.keys())
            counts = [rating_dist[r] for r in ratings]

            # Write data to worksheet (hidden area)
            data_row = 100  # Start at row 100 to keep it out of view
            worksheet.write_row(data_row, 0, ratings)
            worksheet.write_row(data_row + 1, 0, counts)

            # Configure chart
            chart.add_series({
                "name": "レビュー数",
                "categories": [worksheet.name, data_row, 0, data_row, len(ratings) - 1],
                "values": [worksheet.name, data_row + 1, 0, data_row + 1, len(ratings) - 1],
                "fill": {"color": "#4472C4"},
            })

            chart.set_title({"name": title})
            chart.set_x_axis({"name": "評価 (1-5)"})
            chart.set_y_axis({"name": "レビュー数"})
            chart.set_size({"width": 480, "height": 300})
            chart.set_legend({"position": "none"})

            worksheet.insert_chart(chart_position, chart)
            logger.debug(f"Created rating distribution chart at {chart_position}")

        except Exception as e:
            logger.error(f"Failed to create rating chart: {str(e)}")
            raise ChartCreationError(f"Rating chart creation failed: {str(e)}")

    @staticmethod
    def create_sentiment_pie_chart(
        workbook,
        worksheet,
        sentiment_dist: Dict[str, int],
        chart_position: str = "A1",
        title: str = "感情分布"
    ):
        """
        Create sentiment distribution pie chart.

        Args:
            workbook: XlsxWriter workbook object
            worksheet: Worksheet object
            sentiment_dist: Sentiment distribution dictionary
            chart_position: Chart position
            title: Chart title
        """
        try:
            chart = workbook.add_chart({"type": "pie"})

            # Prepare data
            sentiments = ["positive", "neutral", "negative"]
            labels = {"positive": "ポジティブ", "neutral": "ニュートラル", "negative": "ネガティブ"}
            colors = {"positive": "#70AD47", "neutral": "#FFC000", "negative": "#FF0000"}

            data_row = 110
            sentiment_labels = [labels[s] for s in sentiments]
            counts = [sentiment_dist.get(s, 0) for s in sentiments]

            worksheet.write_row(data_row, 0, sentiment_labels)
            worksheet.write_row(data_row + 1, 0, counts)

            # Configure chart
            chart.add_series({
                "name": "感情分析",
                "categories": [worksheet.name, data_row, 0, data_row, len(sentiments) - 1],
                "values": [worksheet.name, data_row + 1, 0, data_row + 1, len(sentiments) - 1],
                "data_labels": {"percentage": True},
                "points": [
                    {"fill": {"color": colors["positive"]}},
                    {"fill": {"color": colors["neutral"]}},
                    {"fill": {"color": colors["negative"]}},
                ],
            })

            chart.set_title({"name": title})
            chart.set_size({"width": 480, "height": 300})

            worksheet.insert_chart(chart_position, chart)
            logger.debug(f"Created sentiment pie chart at {chart_position}")

        except Exception as e:
            logger.error(f"Failed to create sentiment chart: {str(e)}")
            raise ChartCreationError(f"Sentiment chart creation failed: {str(e)}")

    @staticmethod
    def create_keyword_bar_chart(
        workbook,
        worksheet,
        keywords: List[KeywordResult],
        chart_position: str = "A1",
        title: str = "キーワードランキング TOP 10"
    ):
        """
        Create keyword ranking horizontal bar chart.

        Args:
            workbook: XlsxWriter workbook object
            worksheet: Worksheet object
            keywords: List of KeywordResult objects
            chart_position: Chart position
            title: Chart title
        """
        try:
            chart = workbook.add_chart({"type": "bar"})

            # Take top 10 keywords
            top_keywords = keywords[:10]
            if not top_keywords:
                logger.warning("No keywords to chart")
                return

            # Prepare data (reverse order for better visualization)
            keyword_texts = [kw.keyword for kw in reversed(top_keywords)]
            frequencies = [kw.frequency for kw in reversed(top_keywords)]

            data_row = 120
            worksheet.write_column(data_row, 0, keyword_texts)
            worksheet.write_column(data_row, 1, frequencies)

            # Configure chart
            chart.add_series({
                "name": "出現回数",
                "categories": [worksheet.name, data_row, 0, data_row + len(keyword_texts) - 1, 0],
                "values": [worksheet.name, data_row, 1, data_row + len(frequencies) - 1, 1],
                "fill": {"color": "#5B9BD5"},
            })

            chart.set_title({"name": title})
            chart.set_x_axis({"name": "出現回数"})
            chart.set_y_axis({"name": "キーワード"})
            chart.set_size({"width": 600, "height": 400})
            chart.set_legend({"position": "none"})

            worksheet.insert_chart(chart_position, chart)
            logger.debug(f"Created keyword bar chart at {chart_position}")

        except Exception as e:
            logger.error(f"Failed to create keyword chart: {str(e)}")
            raise ChartCreationError(f"Keyword chart creation failed: {str(e)}")

    @staticmethod
    def create_ota_comparison_chart(
        workbook,
        worksheet,
        ota_analyses: List[OTAAnalysis],
        chart_position: str = "A1",
        title: str = "OTA別比較"
    ):
        """
        Create OTA comparison bar chart.

        Args:
            workbook: XlsxWriter workbook object
            worksheet: Worksheet object
            ota_analyses: List of OTAAnalysis objects
            chart_position: Chart position
            title: Chart title
        """
        try:
            chart = workbook.add_chart({"type": "column"})

            if not ota_analyses:
                logger.warning("No OTA analyses to chart")
                return

            # Prepare data
            ota_names = [ota.ota_name for ota in ota_analyses]
            review_counts = [ota.total_reviews for ota in ota_analyses]
            avg_ratings = [ota.average_rating for ota in ota_analyses]

            data_row = 140
            worksheet.write_row(data_row, 0, ota_names)
            worksheet.write_row(data_row + 1, 0, review_counts)
            worksheet.write_row(data_row + 2, 0, avg_ratings)

            # Add review count series
            chart.add_series({
                "name": "レビュー数",
                "categories": [worksheet.name, data_row, 0, data_row, len(ota_names) - 1],
                "values": [worksheet.name, data_row + 1, 0, data_row + 1, len(ota_names) - 1],
                "fill": {"color": "#4472C4"},
            })

            chart.set_title({"name": title})
            chart.set_x_axis({"name": "OTA"})
            chart.set_y_axis({"name": "レビュー数"})
            chart.set_size({"width": 480, "height": 300})

            worksheet.insert_chart(chart_position, chart)
            logger.debug(f"Created OTA comparison chart at {chart_position}")

        except Exception as e:
            logger.error(f"Failed to create OTA comparison chart: {str(e)}")
            raise ChartCreationError(f"OTA comparison chart creation failed: {str(e)}")
