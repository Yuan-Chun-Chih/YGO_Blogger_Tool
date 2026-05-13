from __future__ import annotations

import base64
import html
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

from app.models import CardContext


class HtmlService:
    PRESET_COLORS = [
        "#444444",
        "#990000",
        "#ff0000",
        "#3367d6",
        "#38761d",
    ]
    PRESET_FONT_SIZES = [
        ("標題", 18.0),
        ("小標題", 14.0),
        ("一般", 12.0),
    ]

    def path_to_file_uri(self, path: Path) -> str:
        posix_path = path.resolve().as_posix()
        return f"file:///{quote(posix_path)}"

    def build_card_html_fragment(self, context: CardContext) -> str:
        image_src = self.resolve_editor_image_value(context)
        return self._build_card_fragment(image_src, context.card.name, context.card.desc)

    def build_card_clipboard_fragment(self, context: CardContext) -> str:
        image_src = self.resolve_clipboard_image_value(context)
        return self._build_card_fragment(image_src, context.card.name, context.card.desc)

    def _build_card_fragment(self, image_src: str, card_name: str, card_desc: str) -> str:
        name = html.escape(card_name)
        effect = html.escape(card_desc.strip()).replace("\n", "<br />")
        text_style = (
            "font-family: arial; "
            "font-size: 16px; "
            "color: #444444; "
            "font-weight: bold; "
            "line-height: 1.55; "
            "margin: 0; "
            "padding: 0;"
        )

        return (
            '<div style="margin: 0; padding: 0;">'
            '<div style="text-align: left; margin: 0; padding: 0; line-height: 0;">'
            f'<img src="{html.escape(image_src, quote=True)}" height="400" style="display: block; margin: 0; padding: 0;" />'
            "</div>"
            f'<div style="{text_style}">{name}</div>'
            f'<div style="{text_style}">{effect}</div>'
            "</div>"
        )

    def build_card_plaintext_fragment(self, context: CardContext) -> str:
        return f"{context.card.name.strip()}\n{context.card.desc.strip()}".strip()

    def build_clipboard_html_document(self, fragment: str) -> str:
        return (
            "<html><body>"
            "<!--StartFragment-->"
            f"{fragment}"
            "<!--EndFragment-->"
            "</body></html>"
        )

    def build_cf_html(self, fragment: str) -> bytes:
        html_document = self.build_clipboard_html_document(fragment)
        header_template = (
            "Version:1.0\r\n"
            "StartHTML:{start_html:010d}\r\n"
            "EndHTML:{end_html:010d}\r\n"
            "StartFragment:{start_fragment:010d}\r\n"
            "EndFragment:{end_fragment:010d}\r\n"
        )
        dummy_header = header_template.format(
            start_html=0,
            end_html=0,
            start_fragment=0,
            end_fragment=0,
        )

        start_marker = "<!--StartFragment-->"
        end_marker = "<!--EndFragment-->"

        start_html = len(dummy_header.encode("utf-8"))
        html_bytes = html_document.encode("utf-8")
        start_fragment = start_html + html_document.index(start_marker) + len(start_marker)
        end_fragment = start_html + html_document.index(end_marker)
        end_html = start_html + len(html_bytes)

        header = header_template.format(
            start_html=start_html,
            end_html=end_html,
            start_fragment=start_fragment,
            end_fragment=end_fragment,
        )
        return header.encode("utf-8") + html_bytes

    def resolve_editor_image_value(self, context: CardContext) -> str:
        if context.local_image_path is not None:
            return self.path_to_file_uri(context.local_image_path)
        return f"{{{{IMAGE_URL:{context.card.card_id}}}}}"

    def resolve_clipboard_image_value(self, context: CardContext) -> str:
        if context.local_image_path is None or not context.local_image_path.exists():
            return self.resolve_editor_image_value(context)

        image_bytes = context.local_image_path.read_bytes()
        mime_type = self.detect_image_mime_type(context.local_image_path)
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    def detect_image_mime_type(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if suffix == ".png":
            return "image/png"
        if suffix == ".gif":
            return "image/gif"
        if suffix == ".webp":
            return "image/webp"
        return "application/octet-stream"

    def export_editor_html(self, qt_html: str) -> str:
        body = self.extract_qt_body(qt_html)
        body = self.strip_qt_wrappers(body)
        body = self.replace_local_file_images(body)
        body = self.normalize_html(body)
        return body

    def extract_qt_body(self, qt_html: str) -> str:
        match = re.search(r"<body[^>]*>(.*)</body>", qt_html, flags=re.IGNORECASE | re.DOTALL)
        return match.group(1) if match else qt_html

    def strip_qt_wrappers(self, html_text: str) -> str:
        cleaned = html_text
        cleaned = re.sub(r"</?meta[^>]*>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<style.*?</style>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"</?html[^>]*>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</?head[^>]*>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<body[^>]*>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"</body>", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.replace("-qt-paragraph-type:empty;", "")
        cleaned = re.sub(r'\sstyle=""', "", cleaned, flags=re.IGNORECASE)
        return cleaned

    def replace_local_file_images(self, html_text: str) -> str:
        def repl(match: re.Match[str]) -> str:
            raw_src = match.group(1)
            if raw_src.lower().startswith("file:///"):
                parsed = urlparse(raw_src)
                local_path = Path(unquote(parsed.path))
                return match.group(0).replace(raw_src, f"{{{{IMAGE_URL:{local_path.stem}}}}}")
            return match.group(0)

        return re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', repl, html_text, flags=re.IGNORECASE)

    def normalize_html(self, value: str) -> str:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        normalized = re.sub(r"[ \t]+\n", "\n", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip() + "\n"

    def sanitize_pasted_html(self, raw_html: str) -> str:
        cleaned = raw_html
        cleaned = re.sub(r"<script.*?</script>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()
