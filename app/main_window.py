from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QAction, QColor, QPixmap, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models import AppSettings, CardContext, CardRecord
from app.services.card_repository import CardRepository
from app.services.html_service import HtmlService
from app.services.image_indexer import ImageIndexer
from app.services.settings_service import SettingsService


class HtmlPasteDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("貼上 HTML 草稿")
        self.resize(920, 720)

        layout = QVBoxLayout(self)
        title = QLabel("請將複製的 HTML 內容貼到下方")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText("直接貼上 Blogger 或其他來源的 HTML 內容。")
        layout.addWidget(self.editor)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("取消")
        ok_button = QPushButton("套用")
        ok_button.setObjectName("primaryButton")
        cancel_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self.accept)
        button_row.addWidget(cancel_button)
        button_row.addWidget(ok_button)
        layout.addLayout(button_row)

    def get_html(self) -> str:
        return self.editor.toPlainText()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YGOPRO Blogger Tool")
        self.resize(1560, 980)

        self.project_root = Path(__file__).resolve().parent.parent
        self.settings_service = SettingsService(self.project_root / "settings.json")
        self.html_service = HtmlService()

        self.settings = self._default_settings()
        self.card_repository: CardRepository | None = None
        self.image_indexer: ImageIndexer | None = None
        self.filtered_cards: list[CardRecord] = []

        self._build_ui()
        self._build_menu()
        self._load_settings()
        self.reload_all_sources()

    def _default_settings(self) -> AppSettings:
        return AppSettings(
            cdb_path="",
            pics_path="",
            template_path="",
            output_path=str(self.project_root / "output.html"),
        )

    def _build_ui(self) -> None:
        self._apply_theme()

        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        self.source_status_panel = self._build_source_status_panel()
        root_layout.addWidget(self.source_status_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_search_panel())
        splitter.addWidget(self._build_card_panel())
        splitter.addWidget(self._build_editor_panel())
        splitter.setSizes([300, 380, 840])
        root_layout.addWidget(splitter)

        self.setCentralWidget(root)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f7f9fd,
                    stop: 0.55 #eef3fb,
                    stop: 1 #f9fbff
                );
                color: #232833;
                font-family: Arial;
                font-size: 13px;
            }
            #panelCard {
                background: #ffffff;
                border: 1px solid #d9e1ef;
                border-radius: 14px;
            }
            #sectionTitle, #dialogTitle {
                color: #2859c5;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }
            #sourceStatusValueReady {
                color: #38761d;
                font-size: 13px;
                font-weight: 700;
                background: #edf7e8;
                border: 1px solid #cfe3c4;
                border-radius: 999px;
                padding: 3px 10px;
            }
            #sourceStatusValueMissing {
                color: #990000;
                font-size: 13px;
                font-weight: 700;
                background: #fdecec;
                border: 1px solid #f3caca;
                border-radius: 999px;
                padding: 3px 10px;
            }
            #sourceStatusPath {
                color: #5c6676;
                font-size: 12px;
                background: transparent;
            }
            #cardMetaName {
                color: #202631;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
            }
            #cardMetaId {
                color: #6a7382;
                font-size: 12px;
                font-weight: 700;
                background: #eef3fb;
                border: 1px solid #d8e0ef;
                border-radius: 999px;
                padding: 3px 8px;
            }
            QLabel {
                background: transparent;
                color: #232833;
            }
            QLineEdit, QTextEdit, QListWidget, QComboBox {
                background: #ffffff;
                color: #1f2430;
                border: 1px solid #cfd8e6;
                border-radius: 10px;
                padding: 7px 9px;
                selection-background-color: #dbe7ff;
            }
            QListWidget::item {
                padding: 7px 8px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #e8f0ff;
                color: #2859c5;
            }
            QPushButton {
                background: #ffffff;
                color: #1f2430;
                border: 1px solid #ccd5e3;
                border-radius: 10px;
                padding: 8px 12px;
                min-height: 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #f4f7fc;
                border-color: #b8c5da;
            }
            QPushButton:pressed {
                background: #ebf0f8;
            }
            QPushButton#primaryButton {
                background: #3367d6;
                color: #ffffff;
                border: 1px solid #3367d6;
            }
            QPushButton#primaryButton:hover {
                background: #2959c7;
            }
            QPushButton#toolbarButton {
                min-width: 36px;
            }
            QMenuBar {
                background: #ffffff;
                color: #232833;
                border-bottom: 1px solid #dde4ef;
            }
            QMenuBar::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #edf3ff;
            }
            QMenu {
                background: #ffffff;
                color: #232833;
                border: 1px solid #d2dbea;
            }
            QMenu::item:selected {
                background: #edf3ff;
            }
            QSplitter::handle {
                background: #dde5f1;
                width: 6px;
            }
            """
        )

    def _build_source_status_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title = QLabel("資料來源狀態")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        cdb_row = QHBoxLayout()
        cdb_row.setSpacing(8)
        cdb_row.addWidget(QLabel("cards.cdb"))
        self.cdb_status_label = QLabel()
        cdb_row.addWidget(self.cdb_status_label)
        self.cdb_path_label = QLabel()
        self.cdb_path_label.setObjectName("sourceStatusPath")
        self.cdb_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cdb_row.addWidget(self.cdb_path_label, 1)
        layout.addLayout(cdb_row)

        pics_row = QHBoxLayout()
        pics_row.setSpacing(8)
        pics_row.addWidget(QLabel("pics/"))
        self.pics_status_label = QLabel()
        pics_row.addWidget(self.pics_status_label)
        self.pics_path_label = QLabel()
        self.pics_path_label.setObjectName("sourceStatusPath")
        self.pics_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        pics_row.addWidget(self.pics_path_label, 1)
        layout.addLayout(pics_row)

        return panel

    def _build_search_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("卡片搜尋")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("搜尋"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("輸入卡名搜尋")
        self.search_edit.textChanged.connect(self._refresh_card_list)
        search_row.addWidget(self.search_edit)
        layout.addLayout(search_row)

        self.card_list = QListWidget()
        self.card_list.currentRowChanged.connect(self._on_card_selected)
        layout.addWidget(self.card_list, 1)

        return panel

    def _build_card_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        self.card_name_label = QLabel("-")
        self.card_name_label.setObjectName("cardMetaName")
        self.card_name_label.setWordWrap(True)
        self.card_name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        meta_row.addWidget(self.card_name_label, 1)

        self.card_image_id_label = QLabel("-")
        self.card_image_id_label.setObjectName("cardMetaId")
        self.card_image_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        meta_row.addWidget(self.card_image_id_label, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(meta_row)

        self.card_image_preview = QLabel()
        self.card_image_preview.setMinimumSize(190, 280)
        self.card_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_image_preview.setStyleSheet(
            "background:#fbfcff; border:1px solid #d5deed; border-radius:12px;"
        )
        layout.addWidget(self.card_image_preview, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.effect_preview = QTextEdit()
        self.effect_preview.setReadOnly(True)
        self.effect_preview.setMinimumHeight(260)
        layout.addWidget(self.effect_preview, 1)

        self.copy_card_button = QPushButton("複製圖片與文字")
        self.copy_card_button.setObjectName("primaryButton")
        self.copy_card_button.clicked.connect(self.copy_card_block)
        layout.addWidget(self.copy_card_button)

        return panel

    def _build_editor_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        action_row = QHBoxLayout()
        import_button = QPushButton("貼上 HTML 草稿")
        import_button.clicked.connect(self.import_html_draft)
        copy_button = QPushButton("複製匯出 HTML")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self.copy_export_html)
        action_row.addWidget(import_button)
        action_row.addWidget(copy_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)

        toolbar_row = QHBoxLayout()
        toolbar_row.setSpacing(8)

        bold_button = QPushButton("B")
        bold_button.setObjectName("toolbarButton")
        italic_button = QPushButton("I")
        italic_button.setObjectName("toolbarButton")
        underline_button = QPushButton("U")
        underline_button.setObjectName("toolbarButton")
        bold_button.clicked.connect(self.toggle_bold)
        italic_button.clicked.connect(self.toggle_italic)
        underline_button.clicked.connect(self.toggle_underline)
        toolbar_row.addWidget(bold_button)
        toolbar_row.addWidget(italic_button)
        toolbar_row.addWidget(underline_button)

        self.size_combo = QComboBox()
        self.size_combo.addItem("字級")
        for label, _ in self.html_service.PRESET_FONT_SIZES:
            self.size_combo.addItem(label)
        self.size_combo.currentIndexChanged.connect(self.apply_preset_font_size)
        toolbar_row.addWidget(self.size_combo)

        for color in self.html_service.PRESET_COLORS:
            color_button = QPushButton()
            color_button.setFixedSize(28, 28)
            color_button.setStyleSheet(
                f"background-color: {color}; border: 1px solid #bdbdbd; border-radius: 8px;"
            )
            color_button.clicked.connect(
                lambda _checked=False, value=color: self.apply_text_color(value)
            )
            toolbar_row.addWidget(color_button)

        clear_format_button = QPushButton("清除格式")
        clear_format_button.clicked.connect(self.clear_current_format)
        toolbar_row.addWidget(clear_format_button)
        toolbar_row.addStretch(1)
        layout.addLayout(toolbar_row)

        self.html_editor = QTextEdit()
        self.html_editor.setAcceptRichText(True)
        self.html_editor.setPlaceholderText(
            "直接在這裡編輯文章內容，或先貼上 HTML 草稿後再整理。"
        )
        layout.addWidget(self.html_editor, 1)

        return panel

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("檔案")
        import_html_action = QAction("貼上 HTML 草稿", self)
        import_html_action.triggered.connect(self.import_html_draft)
        copy_action = QAction("複製匯出 HTML", self)
        copy_action.triggered.connect(self.copy_export_html)
        file_menu.addAction(import_html_action)
        file_menu.addAction(copy_action)

        edit_menu = self.menuBar().addMenu("編輯")
        copy_card_action = QAction("複製圖片與文字", self)
        copy_card_action.triggered.connect(self.copy_card_block)
        edit_menu.addAction(copy_card_action)

        sources_menu = self.menuBar().addMenu("資料來源")
        pick_cdb_action = QAction("選擇 cards.cdb", self)
        pick_cdb_action.triggered.connect(self._pick_cdb)
        pick_pics_action = QAction("選擇 pics 資料夾", self)
        pick_pics_action.triggered.connect(self._pick_pics)
        reload_sources_action = QAction("重新載入資料來源", self)
        reload_sources_action.triggered.connect(self.reload_all_sources)
        sources_menu.addAction(pick_cdb_action)
        sources_menu.addAction(pick_pics_action)
        sources_menu.addAction(reload_sources_action)

    def _load_settings(self) -> None:
        loaded = self.settings_service.load()
        defaults = self._default_settings()
        self.settings = AppSettings(
            cdb_path=loaded.cdb_path if loaded.cdb_path and Path(loaded.cdb_path).exists() else defaults.cdb_path,
            pics_path=loaded.pics_path if loaded.pics_path and Path(loaded.pics_path).exists() else defaults.pics_path,
            template_path="",
            output_path=loaded.output_path or defaults.output_path,
        )

    def _save_settings(self) -> None:
        self.settings_service.save(self.settings)

    def _set_source_status(
        self,
        status_label: QLabel,
        path_label: QLabel,
        is_ready: bool,
        ready_text: str,
        missing_text: str,
        path_value: str,
    ) -> None:
        status_label.setText(ready_text if is_ready else missing_text)
        status_label.setObjectName("sourceStatusValueReady" if is_ready else "sourceStatusValueMissing")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)
        path_label.setText(path_value if path_value else "未選擇")

    def _update_source_status_panel(self) -> None:
        cdb_path = self.settings.cdb_path.strip()
        pics_path = self.settings.pics_path.strip()
        has_cdb = bool(cdb_path and Path(cdb_path).exists())
        has_pics = bool(pics_path and Path(pics_path).exists())

        self._set_source_status(
            self.cdb_status_label,
            self.cdb_path_label,
            has_cdb,
            "已選擇",
            "未選擇",
            cdb_path,
        )
        self._set_source_status(
            self.pics_status_label,
            self.pics_path_label,
            has_pics,
            "已選擇",
            "未選擇",
            pics_path,
        )

        self.source_status_panel.setVisible(not (has_cdb and has_pics))

    def _pick_cdb(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 cards.cdb",
            self.settings.cdb_path,
            "CDB (*.cdb);;All Files (*)",
        )
        if file_path:
            self.settings.cdb_path = file_path
            self._save_settings()
            self.reload_all_sources()

    def _pick_pics(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "選擇 pics 資料夾",
            self.settings.pics_path,
        )
        if directory:
            self.settings.pics_path = directory
            self._save_settings()
            self.reload_all_sources()

    def reload_all_sources(self) -> None:
        cdb_path = self.settings.cdb_path.strip()
        pics_path = self.settings.pics_path.strip()
        self._update_source_status_panel()

        if not cdb_path or not Path(cdb_path).exists():
            self.card_repository = None
            self.image_indexer = None
            self._show_no_data_state()
            self.statusBar().showMessage("尚未選擇 cards.cdb。", 5000)
            return

        try:
            self.card_repository = CardRepository(cdb_path)
            self.card_repository.load()

            if pics_path and Path(pics_path).exists():
                self.image_indexer = ImageIndexer(pics_path)
                self.image_indexer.build()
            else:
                self.image_indexer = None

            self._refresh_card_list()
            self._update_source_status_panel()
            self.statusBar().showMessage("資料來源已重新載入。", 5000)
        except Exception as exc:
            self.card_repository = None
            self.image_indexer = None
            self._show_no_data_state()
            self._update_source_status_panel()
            QMessageBox.critical(self, "載入失敗", str(exc))

    def import_html_draft(self) -> None:
        dialog = HtmlPasteDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        raw_html = dialog.get_html().strip()
        if not raw_html:
            return

        cleaned_html = self.html_service.sanitize_pasted_html(raw_html)
        self.html_editor.setHtml(cleaned_html)
        self.statusBar().showMessage("HTML 草稿已載入編輯器。", 5000)

    def _refresh_card_list(self) -> None:
        keyword = self.search_edit.text().strip()
        if self.card_repository is None:
            self._show_no_data_state()
            return

        self.filtered_cards = self.card_repository.search(keyword)
        self.card_list.setEnabled(True)
        self.card_list.clear()
        for card in self.filtered_cards[:500]:
            self.card_list.addItem(QListWidgetItem(card.name))

        if self.filtered_cards:
            self.card_list.setCurrentRow(0)
        else:
            self._update_card_details(None)

    def _show_no_data_state(self) -> None:
        self.filtered_cards = []
        self.card_list.clear()
        self.card_list.addItem("沒有資料請選擇資料來源。")
        self.card_list.setEnabled(False)
        self.card_name_label.setText("-")
        self.card_image_id_label.setText("-")
        self.card_image_preview.clear()
        self.effect_preview.setPlainText("沒有資料請選擇資料來源。")

    def _on_card_selected(self, index: int) -> None:
        if index < 0 or index >= len(self.filtered_cards):
            self._update_card_details(None)
            return
        self._update_card_details(self.filtered_cards[index])

    def _update_card_details(self, card: CardRecord | None) -> None:
        if card is None:
            self.card_name_label.setText("-")
            self.card_image_id_label.setText("-")
            self.card_image_preview.clear()
            self.effect_preview.clear()
            return

        self.card_name_label.setText(card.name)
        self.card_image_id_label.setText(str(card.card_id))
        self.effect_preview.setPlainText(card.desc)

        image_path = self._get_card_image(card)
        if image_path and image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self.card_image_preview.setPixmap(
                    pixmap.scaled(
                        190,
                        280,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                return

        self.card_image_preview.clear()

    def _get_selected_card(self) -> CardRecord | None:
        row = self.card_list.currentRow()
        if row < 0 or row >= len(self.filtered_cards):
            return None
        return self.filtered_cards[row]

    def _get_card_image(self, card: CardRecord) -> Path | None:
        if self.image_indexer is None:
            return None
        return self.image_indexer.get(card.card_id)

    def _build_card_context(self) -> CardContext | None:
        card = self._get_selected_card()
        if card is None:
            QMessageBox.warning(self, "尚未選擇卡片", "請先在左側選擇一張卡片。")
            return None
        return CardContext(
            card=card,
            local_image_path=self._get_card_image(card),
            public_image_url="",
            comment="",
        )

    def copy_card_block(self) -> None:
        context = self._build_card_context()
        if context is None:
            return

        html_fragment = self.html_service.build_card_clipboard_fragment(context)
        plain_text = self.html_service.build_card_plaintext_fragment(context)
        cf_html = self.html_service.build_cf_html(html_fragment)

        try:
            import win32clipboard
            import win32con

            html_format = win32clipboard.RegisterClipboardFormat("HTML Format")
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, plain_text)
                win32clipboard.SetClipboardData(html_format, cf_html)
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            mime_data = QMimeData()
            mime_data.setHtml(self.html_service.build_card_html_fragment(context))
            mime_data.setText(plain_text)
            QApplication.clipboard().setMimeData(mime_data)

        self.statusBar().showMessage("已複製可貼到 Word 的卡片圖片與文字。", 5000)

    def merge_format(self, formatter: QTextCharFormat) -> None:
        cursor = self.html_editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(formatter)
        self.html_editor.mergeCurrentCharFormat(formatter)

    def toggle_bold(self) -> None:
        formatter = QTextCharFormat()
        formatter.setFontWeight(700 if self.html_editor.fontWeight() != 700 else 400)
        self.merge_format(formatter)

    def toggle_italic(self) -> None:
        formatter = QTextCharFormat()
        formatter.setFontItalic(not self.html_editor.fontItalic())
        self.merge_format(formatter)

    def toggle_underline(self) -> None:
        formatter = QTextCharFormat()
        formatter.setFontUnderline(not self.html_editor.fontUnderline())
        self.merge_format(formatter)

    def apply_text_color(self, color_value: str) -> None:
        formatter = QTextCharFormat()
        formatter.setForeground(QColor(color_value))
        self.merge_format(formatter)

    def apply_preset_font_size(self, index: int) -> None:
        if index <= 0:
            return
        _, size = self.html_service.PRESET_FONT_SIZES[index - 1]
        formatter = QTextCharFormat()
        formatter.setFontPointSize(size)
        self.merge_format(formatter)

    def clear_current_format(self) -> None:
        formatter = QTextCharFormat()
        formatter.setFontWeight(400)
        formatter.setFontItalic(False)
        formatter.setFontUnderline(False)
        formatter.setForeground(QColor("#444444"))
        formatter.setFontPointSize(self.html_service.PRESET_FONT_SIZES[2][1])
        self.merge_format(formatter)

    def build_export_html(self) -> str:
        return self.html_service.export_editor_html(self.html_editor.toHtml())

    def copy_export_html(self) -> None:
        QApplication.clipboard().setText(self.build_export_html())
        self.statusBar().showMessage("已複製匯出 HTML。", 5000)


def run() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
