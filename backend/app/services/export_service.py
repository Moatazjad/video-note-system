from pathlib import Path
from typing import Optional, Tuple
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from arabic_reshaper import reshape
from bidi.algorithm import get_display

from app.core.config import settings


class ExportService:
    @staticmethod
    def save_markdown(
        content: str,
        filename: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        output_dir = output_dir or settings.OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        markdown_path = output_dir / f"{filename}.md"

        try:
            markdown_path.write_text(content, encoding="utf-8")
            return markdown_path
        except Exception as exc:
            raise RuntimeError(f"Failed to save markdown: {exc}") from exc

    @staticmethod
    def markdown_to_pdf(
        content: str,
        filename: str,
        output_dir: Optional[Path] = None,
        language: str = "en",
    ) -> Path:
        output_dir = output_dir or settings.OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{filename}.pdf"

        try:
            arabic_font_path = settings.FONT_DIR / "Amiri-Regular.ttf"

            if language == "ar":
                if not arabic_font_path.exists():
                    raise RuntimeError(
                        "Arabic font file not found (Amiri-Regular.ttf)."
                    )

                if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(
                        TTFont("ArabicFont", str(arabic_font_path))
                    )

            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            base_style = ParagraphStyle(
                "BaseStyle",
                parent=styles["Normal"],
                alignment=TA_RIGHT if language == "ar" else TA_LEFT,
                fontSize=12,
                leading=18,
                fontName="ArabicFont" if language == "ar" else "Helvetica",
            )

            lines = content.splitlines()

            for line in lines:
                if not line.strip():
                    story.append(Spacer(1, 12))
                    continue

                header_match = re.match(r"^(#+)\s*(.*)", line)
                if header_match:
                    level = len(header_match.group(1))
                    text = header_match.group(2).strip()

                    if language == "ar":
                        text = get_display(reshape(text))

                    header_style = ParagraphStyle(
                        f"Header{level}",
                        parent=base_style,
                        fontSize=max(18 - level * 2, 12),
                        leading=20,
                        spaceAfter=12,
                        fontName=(
                            "ArabicFont"
                            if language == "ar"
                            else "Helvetica-Bold"
                        ),
                    )

                    story.append(Paragraph(text, header_style))
                    continue

                if language == "ar":
                    line = get_display(reshape(line))

                story.append(Paragraph(line, base_style))

            doc.build(story)
            return pdf_path

        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate PDF: {exc}"
            ) from exc

    @staticmethod
    def export_both(
        content: str,
        filename: str,
        output_dir: Optional[Path] = None,
        language: str = "en",
    ) -> Tuple[Path, Path]:
        md_path = ExportService.save_markdown(
            content, filename, output_dir
        )
        pdf_path = ExportService.markdown_to_pdf(
            content, filename, output_dir, language
        )
        return md_path, pdf_path

    @staticmethod
    def export(
        video_id: int,
        notes: str,
        language: str = "en",
    ) -> Tuple[Path, Path]:
        filename = f"video_{video_id}_notes"

        return ExportService.export_both(
            content=notes,
            filename=filename,
            language=language,
        )
