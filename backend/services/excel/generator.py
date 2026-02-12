"""
Main Excel report generator.
"""
from pathlib import Path
from datetime import datetime
import time
from loguru import logger

try:
    import xlsxwriter
except ImportError:
    logger.warning("xlsxwriter not installed, using mock mode")
    xlsxwriter = None

from backend.models.review import Review
from backend.models.analysis_result import AnalysisResult
from backend.services.excel.sheets import SheetCreator
from backend.config import settings
from backend.utils.exceptions import ExcelGenerationException
from backend.utils.helpers import sanitize_filename


class ExcelReportGenerator:
    """Generator for comprehensive Excel reports."""

    def __init__(self):
        """Initialize Excel report generator."""
        self.output_dir = settings.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        reviews: list[Review],
        analysis_result: AnalysisResult,
        hotel_name: str,
        include_charts: bool = True,
        include_raw_data: bool = True
    ) -> Path:
        """
        Generate comprehensive Excel report.

        Args:
            reviews: List of reviews
            analysis_result: Analysis results
            hotel_name: Hotel name
            include_charts: Whether to include charts
            include_raw_data: Whether to include raw review data

        Returns:
            Path to generated Excel file

        Raises:
            ExcelGenerationException: If generation fails
        """
        logger.info(f"Generating Excel report for {hotel_name}")
        start_time = time.time()

        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_hotel_name = sanitize_filename(hotel_name)
            filename = f"hotel_review_report_{safe_hotel_name}_{timestamp}.xlsx"
            filepath = self.output_dir / filename

            # Check if xlsxwriter is available
            if xlsxwriter is None:
                logger.warning("xlsxwriter not installed, creating mock report")
                return self._create_mock_report(filepath, reviews, analysis_result)

            # Create workbook
            workbook = xlsxwriter.Workbook(str(filepath))

            # Create sheets
            self._create_all_sheets(
                workbook,
                reviews,
                analysis_result,
                hotel_name,
                include_charts,
                include_raw_data
            )

            # Close workbook
            workbook.close()

            file_size = filepath.stat().st_size
            elapsed = time.time() - start_time

            logger.info(
                f"✅ Excel report generated: {filename} "
                f"({file_size / 1024:.1f}KB) in {elapsed:.2f}s"
            )

            return filepath

        except Exception as e:
            logger.error(f"Failed to generate Excel report: {str(e)}")
            raise ExcelGenerationException(f"Excel report generation failed: {str(e)}")

    def _create_all_sheets(
        self,
        workbook,
        reviews: list[Review],
        analysis_result: AnalysisResult,
        hotel_name: str,
        include_charts: bool,
        include_raw_data: bool
    ):
        """
        Create all sheets in the workbook.

        Args:
            workbook: XlsxWriter workbook object
            reviews: List of reviews
            analysis_result: Analysis results
            hotel_name: Hotel name
            include_charts: Whether to include charts
            include_raw_data: Whether to include raw data
        """
        # 1. Summary sheet (always included)
        SheetCreator.create_summary_sheet(
            workbook,
            analysis_result,
            hotel_name
        )

        # 2. Reviews list sheet (if raw data requested)
        if include_raw_data and reviews:
            SheetCreator.create_reviews_sheet(
                workbook,
                reviews
            )

        # 3. Keywords analysis sheet
        if analysis_result.top_keywords:
            SheetCreator.create_keywords_sheet(
                workbook,
                analysis_result
            )

        # 4. OTA-specific sheets
        for ota_analysis in analysis_result.ota_analyses:
            # Filter reviews for this OTA
            ota_reviews = [
                r for r in reviews
                if r.source.value == ota_analysis.ota_name
            ]

            SheetCreator.create_ota_sheet(
                workbook,
                ota_analysis,
                ota_reviews
            )

    def _create_mock_report(
        self,
        filepath: Path,
        reviews: list[Review],
        analysis_result: AnalysisResult
    ) -> Path:
        """
        Create a mock report (text file) when xlsxwriter is not available.

        Args:
            filepath: Output file path
            reviews: List of reviews
            analysis_result: Analysis results

        Returns:
            Path to mock file
        """
        # Create text file instead
        mock_filepath = filepath.with_suffix(".txt")

        with open(mock_filepath, "w", encoding="utf-8") as f:
            f.write("Hotel Review Analysis Report (Mock)\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Reviews: {analysis_result.total_reviews}\n")
            f.write(f"Average Rating: {analysis_result.average_rating:.2f}\n")
            f.write(f"Average Sentiment: {analysis_result.average_sentiment:.3f}\n\n")

            f.write("Sentiment Distribution:\n")
            for sentiment, count in analysis_result.sentiment_distribution.items():
                f.write(f"  {sentiment}: {count}\n")

            f.write("\nTop Keywords:\n")
            for i, kw in enumerate(analysis_result.top_keywords[:10], 1):
                f.write(f"  {i}. {kw.keyword} ({kw.frequency} times)\n")

            f.write("\nOTA Breakdown:\n")
            for ota in analysis_result.ota_analyses:
                f.write(f"  {ota.ota_name}: {ota.total_reviews} reviews (avg: {ota.average_rating:.2f})\n")

        logger.info(f"Mock report created: {mock_filepath}")
        return mock_filepath

    def get_recent_reports(self, limit: int = 10) -> list[dict]:
        """
        Get list of recently generated reports.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of report info dictionaries
        """
        try:
            # Find all Excel and text files in output directory
            files = list(self.output_dir.glob("hotel_review_report_*.*"))

            # Sort by modification time (newest first)
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Take top N
            files = files[:limit]

            # Build info list
            reports = []
            for filepath in files:
                stat = filepath.stat()
                reports.append({
                    "filename": filepath.name,
                    "filepath": str(filepath),
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            return reports

        except Exception as e:
            logger.error(f"Failed to get recent reports: {str(e)}")
            return []

    def delete_report(self, filename: str) -> bool:
        """
        Delete a report file.

        Args:
            filename: Filename to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.output_dir / filename

            # Security check: ensure file is in output directory
            if not filepath.resolve().parent == self.output_dir.resolve():
                logger.error(f"Security violation: attempted to delete file outside output directory")
                return False

            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted report: {filename}")
                return True
            else:
                logger.warning(f"Report not found: {filename}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete report: {str(e)}")
            return False
