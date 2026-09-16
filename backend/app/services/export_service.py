from pathlib import Path
from typing import Optional, Tuple
import re
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from arabic_reshaper import reshape
from bidi.algorithm import get_display

from app.core.config import settings

BULLET_RE = re.compile(r"^[-*]\s+(.*)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


WHOLE_LINE_BOLD_RE = re.compile(r"^\*\*(.+)\*\*$")


def _render_inline(text: str, language: str) -> str:
    """Escape raw LLM output for ReportLab's markup parser, then apply the
    subset of Markdown we support. Bold markup is only added for LTR text:
    inserting <b> tags before bidi reordering (Arabic) would scatter the
    tags away from the text they wrap, since get_display() reorders
    characters for visual display -- see the Arabic bold handling in
    markdown_to_pdf(), which swaps the whole paragraph's font instead."""
    rendered = escape(text)

    if language != "ar":
        rendered = BOLD_RE.sub(r"<b>\1</b>", rendered)

    if language == "ar":
        # base_dir='R' pins the paragraph's bidi base direction to RTL
        # instead of relying on auto-detection from the first strong
        # character. Auto-detection is what actually breaks mixed
        # Arabic/Latin/number text: a line that happens to start with a
        # Latin acronym, an inline English term, or a leading digit can
        # get auto-detected as LTR, scrambling the whole line's word
        # order even though individual words are still shaped correctly.
        rendered = get_display(reshape(rendered), base_dir="R")

    return rendered


def _render_plain(text: str, language: str) -> str:
    """Fallback for malformed inline markup (e.g. an odd number of ** in a
    line): escape and reshape, but never insert markup tags."""
    rendered = escape(text)
    if language == "ar":
        rendered = get_display(reshape(rendered), base_dir="R")
    return rendered


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
            arabic_bold_font_path = settings.FONT_DIR / "Amiri-1.003" / "Amiri-Bold.ttf"

            if language == "ar":
                if not arabic_font_path.exists():
                    raise RuntimeError(
                        "Arabic font file not found (Amiri-Regular.ttf)."
                    )

                if "ArabicFont" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(
                        TTFont("ArabicFont", str(arabic_font_path))
                    )

                if (
                    arabic_bold_font_path.exists()
                    and "ArabicFont-Bold" not in pdfmetrics.getRegisteredFontNames()
                ):
                    pdfmetrics.registerFont(
                        TTFont("ArabicFont-Bold", str(arabic_bold_font_path))
                    )

            arabic_bold_available = (
                language == "ar" and "ArabicFont-Bold" in pdfmetrics.getRegisteredFontNames()
            )
            arabic_header_font = "ArabicFont-Bold" if arabic_bold_available else "ArabicFont"

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

                    header_style = ParagraphStyle(
                        f"Header{level}",
                        parent=base_style,
                        fontSize=max(18 - level * 2, 12),
                        leading=20,
                        spaceAfter=12,
                        fontName=(
                            arabic_header_font
                            if language == "ar"
                            else "Helvetica-Bold"
                        ),
                    )

                    try:
                        story.append(
                            Paragraph(_render_inline(text, language), header_style)
                        )
                    except Exception:
                        story.append(
                            Paragraph(_render_plain(text, language), header_style)
                        )
                    continue

                bullet_match = BULLET_RE.match(line)
                inner = bullet_match.group(1) if bullet_match else line

                # A bullet/line that is ENTIRELY wrapped in **...** (a common
                # LLM "key term" pattern) gets rendered as a whole bold
                # paragraph via font swap, rather than attempting inline <b>
                # injection -- which is unsafe for Arabic (see _render_inline).
                whole_bold_match = WHOLE_LINE_BOLD_RE.match(inner.strip())
                if whole_bold_match:
                    bold_prefix = "• " if bullet_match else ""
                    text = bold_prefix + whole_bold_match.group(1)
                    style = ParagraphStyle(
                        "BoldLine",
                        parent=base_style,
                        fontName=(
                            arabic_header_font if language == "ar" else "Helvetica-Bold"
                        ),
                    )
                    try:
                        story.append(Paragraph(_render_plain(text, language), style))
                    except Exception:
                        story.append(Paragraph(_render_plain(text, language), base_style))
                    continue

                text = f"• {bullet_match.group(1)}" if bullet_match else line

                try:
                    story.append(
                        Paragraph(_render_inline(text, language), base_style)
                    )
                except Exception:
                    story.append(
                        Paragraph(_render_plain(text, language), base_style)
                    )

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
