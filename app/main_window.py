from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
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
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.models import AppSettings, CardContext, CardRecord
from app.services.card_repository import CardRepository
from app.services.constant_service import load_constant_option_labels
from app.services.html_service import HtmlService
from app.services.image_indexer import ImageIndexer
from app.services.setcode_service import SetcodeService
from app.services.settings_service import SettingsService
from app.ui_text import OPTION_LABELS as UI_OPTION_LABELS
from app.ui_text import STRINGS as UI_STRINGS

LANGUAGES = ["zh_TW", "en"]

STRINGS = {
    "zh_TW": {
        "window_title": "YGOPRO Blogger Tool",
        "source_status": "資料來源狀態",
        "selected": "已選擇",
        "not_selected": "未選擇",
        "html_tools": "HTML 格式整理",
        "paste_html": "貼上 HTML 草稿",
        "copy_export_html": "複製匯出 HTML",
        "size_placeholder": "字級",
        "size_title": "標題",
        "size_subtitle": "小標題",
        "size_normal": "一般",
        "clear_format": "清除格式",
        "search_title": "卡片搜尋",
        "search_keyword": "關鍵字",
        "search_placeholder": "輸入卡名或卡號",
        "copy_card": "複製圖片與文字",
        "cdb_editor": "CDB 編輯",
        "cdb_helper": "右側可直接修改 cards.cdb。選項欄位以文字為主，也可直接手動輸入。",
        "effect_placeholder": "效果文",
        "load_current": "載入目前卡",
        "save_changes": "儲存修改",
        "discard_changes": "放棄修改",
        "add_card": "新增卡片",
        "delete_card": "刪除卡片",
        "extra_texts": "texts 擴充（str1 ~ str16）",
        "menu_file": "檔案",
        "menu_edit": "編輯",
        "menu_sources": "資料來源",
        "menu_language": "語言",
        "menu_pick_cdb": "選擇 cards.cdb",
        "menu_pick_pics": "選擇 pics 資料夾",
        "menu_reload_sources": "重新載入資料來源",
        "menu_copy_card": "複製圖片與文字",
        "menu_save_card": "儲存目前卡片修改",
        "language_zh_TW": "繁體中文",
        "language_en": "English",
        "field_id": "id",
        "field_name": "卡名",
        "field_ot": "ot",
        "field_type": "type",
        "field_alias": "alias",
        "field_setcode": "setcode",
        "field_atk": "atk",
        "field_def": "def",
        "field_level": "level",
        "field_race": "race",
        "field_attribute": "attribute",
        "field_category": "category",
        "no_data": "沒有資料請選擇資料來源。",
        "pick_cdb_title": "選擇 cards.cdb",
        "pick_pics_title": "選擇 pics 資料夾",
        "warn_no_card_title": "尚未選擇卡片",
        "warn_no_card_text": "請先從左側清單選擇卡片。",
        "warn_no_repo_title": "沒有可操作的卡片",
        "warn_no_repo_text": "請先載入 cards.cdb 並選擇一張卡片。",
        "copied_word": "已複製可貼到 Word 的卡片圖片與文字。",
        "copied_html": "已複製匯出 HTML。",
        "loaded_html": "HTML 草稿已載入編輯器。",
        "loaded_sources": "資料來源已重新載入。",
        "missing_cdb": "尚未選擇 cards.cdb。",
        "loaded_editor": "已載入目前卡片到 CDB 編輯區。",
        "reset_editor": "已還原目前卡片的編輯內容。",
        "saved_card": "已儲存卡片修改，並建立備份：{name}",
        "added_card": "已新增卡片，並建立備份：{name}",
        "deleted_card": "已刪除卡片，並建立備份：{name}",
        "save_failed": "儲存失敗",
        "load_failed": "載入失敗",
        "confirm_delete_title": "確認刪除",
        "confirm_delete_text": "確定要刪除這張卡片嗎？\n{id} {name}",
        "field_required": "{name} 不能為空。",
        "name_required": "卡名不能為空。",
        "paste_dialog_title": "貼上 HTML 草稿",
        "paste_dialog_label": "請貼上要整理的 Blogger HTML 草稿",
        "paste_dialog_placeholder": "將 Blogger HTML 原始碼貼到這裡",
        "cancel": "取消",
        "apply": "套用",
    },
    "en": {
        "window_title": "YGOPRO Blogger Tool",
        "source_status": "Source Status",
        "selected": "Selected",
        "not_selected": "Not Selected",
        "html_tools": "HTML Format Tools",
        "paste_html": "Paste HTML Draft",
        "copy_export_html": "Copy Export HTML",
        "size_placeholder": "Size",
        "size_title": "Title",
        "size_subtitle": "Subtitle",
        "size_normal": "Normal",
        "clear_format": "Clear Format",
        "search_title": "Card Search",
        "search_keyword": "Keyword",
        "search_placeholder": "Enter card name or id",
        "copy_card": "Copy Image and Text",
        "cdb_editor": "CDB Editor",
        "cdb_helper": "Edit cards.cdb directly on the right. Option fields are text-first and still accept manual numeric input.",
        "effect_placeholder": "Effect text",
        "load_current": "Load Current Card",
        "save_changes": "Save Changes",
        "discard_changes": "Discard Changes",
        "add_card": "Add Card",
        "delete_card": "Delete Card",
        "extra_texts": "texts extras (str1 ~ str16)",
        "menu_file": "File",
        "menu_edit": "Edit",
        "menu_sources": "Sources",
        "menu_language": "Language",
        "menu_pick_cdb": "Select cards.cdb",
        "menu_pick_pics": "Select pics Folder",
        "menu_reload_sources": "Reload Sources",
        "menu_copy_card": "Copy Image and Text",
        "menu_save_card": "Save Current Card",
        "language_zh_TW": "Traditional Chinese",
        "language_en": "English",
        "field_id": "id",
        "field_name": "Name",
        "field_ot": "ot",
        "field_type": "type",
        "field_alias": "alias",
        "field_setcode": "setcode",
        "field_atk": "atk",
        "field_def": "def",
        "field_level": "level",
        "field_race": "race",
        "field_attribute": "attribute",
        "field_category": "category",
        "no_data": "No data. Please choose a data source.",
        "pick_cdb_title": "Select cards.cdb",
        "pick_pics_title": "Select pics Folder",
        "warn_no_card_title": "No Card Selected",
        "warn_no_card_text": "Please select a card from the list first.",
        "warn_no_repo_title": "No Card Available",
        "warn_no_repo_text": "Please load cards.cdb and select a card first.",
        "copied_word": "Copied card image and text for Word.",
        "copied_html": "Copied exported HTML.",
        "loaded_html": "Loaded HTML draft into the editor.",
        "loaded_sources": "Reloaded data sources.",
        "missing_cdb": "cards.cdb has not been selected.",
        "loaded_editor": "Loaded current card into the CDB editor.",
        "reset_editor": "Reset the editor to the current card values.",
        "saved_card": "Saved card changes and created backup: {name}",
        "added_card": "Added card and created backup: {name}",
        "deleted_card": "Deleted card and created backup: {name}",
        "save_failed": "Save Failed",
        "load_failed": "Load Failed",
        "confirm_delete_title": "Confirm Delete",
        "confirm_delete_text": "Delete this card?\n{id} {name}",
        "field_required": "{name} cannot be empty.",
        "name_required": "Card name cannot be empty.",
        "paste_dialog_title": "Paste HTML Draft",
        "paste_dialog_label": "Paste the Blogger HTML draft to normalize",
        "paste_dialog_placeholder": "Paste Blogger HTML source here",
        "cancel": "Cancel",
        "apply": "Apply",
    },
}

OPTION_LABELS = {
    "ot": {
        1: {"zh_TW": "OCG / TCG", "en": "OCG / TCG"},
        2: {"zh_TW": "動畫", "en": "Anime"},
        4: {"zh_TW": "非法", "en": "Illegal"},
        8: {"zh_TW": "遊戲", "en": "Video Game"},
        16: {"zh_TW": "自訂", "en": "Custom"},
    },
    "attribute": {
        0: {"zh_TW": "無", "en": "None"},
        1: {"zh_TW": "地屬性", "en": "Earth"},
        2: {"zh_TW": "水屬性", "en": "Water"},
        4: {"zh_TW": "炎屬性", "en": "Fire"},
        8: {"zh_TW": "風屬性", "en": "Wind"},
        16: {"zh_TW": "光屬性", "en": "Light"},
        32: {"zh_TW": "闇屬性", "en": "Dark"},
        64: {"zh_TW": "神屬性", "en": "Divine"},
    },
    "race": {
        1: {"zh_TW": "戰士族", "en": "Warrior"},
        2: {"zh_TW": "魔法使族", "en": "Spellcaster"},
        4: {"zh_TW": "天使族", "en": "Fairy"},
        8: {"zh_TW": "惡魔族", "en": "Fiend"},
        16: {"zh_TW": "不死族", "en": "Zombie"},
        32: {"zh_TW": "機械族", "en": "Machine"},
        64: {"zh_TW": "水族", "en": "Aqua"},
        128: {"zh_TW": "炎族", "en": "Pyro"},
        256: {"zh_TW": "岩石族", "en": "Rock"},
        512: {"zh_TW": "鳥獸族", "en": "Winged Beast"},
        1024: {"zh_TW": "植物族", "en": "Plant"},
        2048: {"zh_TW": "昆蟲族", "en": "Insect"},
        4096: {"zh_TW": "雷族", "en": "Thunder"},
        8192: {"zh_TW": "龍族", "en": "Dragon"},
        16384: {"zh_TW": "獸族", "en": "Beast"},
        32768: {"zh_TW": "獸戰士族", "en": "Beast-Warrior"},
        65536: {"zh_TW": "恐龍族", "en": "Dinosaur"},
        131072: {"zh_TW": "魚族", "en": "Fish"},
        262144: {"zh_TW": "海龍族", "en": "Sea Serpent"},
        524288: {"zh_TW": "爬蟲類族", "en": "Reptile"},
        1048576: {"zh_TW": "念動力族", "en": "Psychic"},
        2097152: {"zh_TW": "幻神獸族", "en": "Divine Beast"},
        4194304: {"zh_TW": "創造神族", "en": "Creator God"},
        8388608: {"zh_TW": "幻龍族", "en": "Wyrm"},
        16777216: {"zh_TW": "電子界族", "en": "Cyberse"},
        33554432: {"zh_TW": "幻想魔族", "en": "Illusion"},
    },
    "type": {
        1: {"zh_TW": "怪獸", "en": "Monster"},
        17: {"zh_TW": "通常怪獸", "en": "Normal Monster"},
        33: {"zh_TW": "效果怪獸", "en": "Effect Monster"},
        49: {"zh_TW": "二重怪獸", "en": "Gemini Monster"},
        65: {"zh_TW": "融合怪獸", "en": "Fusion Monster"},
        97: {"zh_TW": "融合效果", "en": "Fusion Effect"},
        129: {"zh_TW": "儀式怪獸", "en": "Ritual Monster"},
        161: {"zh_TW": "儀式效果", "en": "Ritual Effect"},
        257: {"zh_TW": "陷阱怪獸", "en": "Trap Monster"},
        513: {"zh_TW": "靈魂怪獸", "en": "Spirit Monster"},
        1025: {"zh_TW": "同盟怪獸", "en": "Union Monster"},
        2049: {"zh_TW": "雙重怪獸", "en": "Dual Monster"},
        4097: {"zh_TW": "協調怪獸", "en": "Tuner Monster"},
        8193: {"zh_TW": "同步怪獸", "en": "Synchro Monster"},
        8388641: {"zh_TW": "同步效果", "en": "Synchro Effect"},
        16385: {"zh_TW": "衍生物", "en": "Token"},
        2097185: {"zh_TW": "反轉效果", "en": "Flip Effect"},
        4194337: {"zh_TW": "靈擺效果", "en": "Pendulum Effect"},
        8389137: {"zh_TW": "同步靈擺", "en": "Synchro Pendulum"},
        16777249: {"zh_TW": "連結怪獸", "en": "Link Monster"},
        18874401: {"zh_TW": "連結效果", "en": "Link Effect"},
        67108897: {"zh_TW": "超量怪獸", "en": "Xyz Monster"},
        75497505: {"zh_TW": "超量效果", "en": "Xyz Effect"},
        83886081: {"zh_TW": "靈擺通常", "en": "Pendulum Normal"},
        83886113: {"zh_TW": "靈擺效果怪獸", "en": "Pendulum Effect Monster"},
        16785441: {"zh_TW": "連結靈擺", "en": "Link Pendulum"},
        2: {"zh_TW": "魔法", "en": "Spell"},
        65538: {"zh_TW": "通常魔法", "en": "Normal Spell"},
        131074: {"zh_TW": "速攻魔法", "en": "Quick-Play Spell"},
        262146: {"zh_TW": "永續魔法", "en": "Continuous Spell"},
        524290: {"zh_TW": "裝備魔法", "en": "Equip Spell"},
        1048578: {"zh_TW": "場地魔法", "en": "Field Spell"},
        2097154: {"zh_TW": "儀式魔法", "en": "Ritual Spell"},
        4: {"zh_TW": "陷阱", "en": "Trap"},
        131076: {"zh_TW": "通常陷阱", "en": "Normal Trap"},
        262148: {"zh_TW": "永續陷阱", "en": "Continuous Trap"},
        524292: {"zh_TW": "反擊陷阱", "en": "Counter Trap"},
    },
    "category": {
        0: {"zh_TW": "無", "en": "None"},
        1: {"zh_TW": "破壞怪獸", "en": "Destroy Monster"},
        2: {"zh_TW": "破壞魔陷", "en": "Destroy Spell/Trap"},
        4: {"zh_TW": "回手", "en": "Bounce"},
        8: {"zh_TW": "檢索", "en": "Search"},
        16: {"zh_TW": "抽牌", "en": "Draw"},
        32: {"zh_TW": "特殊召喚", "en": "Special Summon"},
        64: {"zh_TW": "變更表示", "en": "Change Position"},
        128: {"zh_TW": "控制權變更", "en": "Control"},
    },
}

STRINGS = UI_STRINGS
OPTION_LABELS = UI_OPTION_LABELS.copy()
CONSTANT_OPTION_LABELS = load_constant_option_labels(Path(__file__).resolve().parent.parent / "data")
for option_key, option_values in CONSTANT_OPTION_LABELS.items():
    if option_values:
        OPTION_LABELS[option_key] = option_values

TYPE_FLAG_LABELS = OPTION_LABELS["type"]
        
LEGACY_TYPE_FLAG_LABELS = {
    1: {"zh_TW": "怪獸", "en": "Monster"},
    2: {"zh_TW": "魔法", "en": "Spell"},
    4: {"zh_TW": "陷阱", "en": "Trap"},
    16: {"zh_TW": "通常", "en": "Normal"},
    32: {"zh_TW": "效果", "en": "Effect"},
    64: {"zh_TW": "融合", "en": "Fusion"},
    128: {"zh_TW": "儀式", "en": "Ritual"},
    512: {"zh_TW": "靈魂", "en": "Spirit"},
    1024: {"zh_TW": "聯合", "en": "Union"},
    2048: {"zh_TW": "二重", "en": "Gemini"},
    4096: {"zh_TW": "協調", "en": "Tuner"},
    8192: {"zh_TW": "同步", "en": "Synchro"},
    16384: {"zh_TW": "衍生物", "en": "Token"},
    65536: {"zh_TW": "通常魔法/陷阱", "en": "Normal Spell/Trap"},
    131072: {"zh_TW": "速攻魔法", "en": "Quick-Play"},
    262144: {"zh_TW": "永續", "en": "Continuous"},
    524288: {"zh_TW": "裝備/反擊", "en": "Equip/Counter"},
    1048576: {"zh_TW": "場地", "en": "Field"},
    2097152: {"zh_TW": "反轉", "en": "Flip"},
    4194304: {"zh_TW": "卡通", "en": "Toon"},
    8388608: {"zh_TW": "超量", "en": "Xyz"},
    16777216: {"zh_TW": "靈擺", "en": "Pendulum"},
    67108864: {"zh_TW": "連結", "en": "Link"},
}

CATEGORY_FLAG_LABELS = OPTION_LABELS["category"]

LEGACY_CATEGORY_FLAG_LABELS = {
    1: {"zh_TW": "破壞怪獸", "en": "Destroy Monster"},
    2: {"zh_TW": "破壞魔陷", "en": "Destroy Spell/Trap"},
    4: {"zh_TW": "回手/彈回", "en": "Bounce"},
    8: {"zh_TW": "檢索", "en": "Search"},
    16: {"zh_TW": "抽牌", "en": "Draw"},
    32: {"zh_TW": "特殊召喚", "en": "Special Summon"},
    64: {"zh_TW": "變更表示形式", "en": "Change Position"},
    128: {"zh_TW": "控制權", "en": "Control"},
    256: {"zh_TW": "墓地回收", "en": "Recycle Grave"},
    512: {"zh_TW": "除外", "en": "Banish"},
    1024: {"zh_TW": "加入手牌", "en": "To Hand"},
    2048: {"zh_TW": "回到牌組", "en": "To Deck"},
    4096: {"zh_TW": "送去墓地", "en": "Send to Grave"},
    8192: {"zh_TW": "自壞", "en": "Self Destroy"},
    16384: {"zh_TW": "無效", "en": "Negate"},
    32768: {"zh_TW": "等級變更", "en": "Change Level"},
    65536: {"zh_TW": "屬性變更", "en": "Change Attribute"},
    131072: {"zh_TW": "種族變更", "en": "Change Race"},
}

FIELD_LABEL_OVERRIDES = {
    "zh_TW": {
        "field_id": "卡片密碼",
        "field_type": "卡片類型",
        "field_alias": "同名卡",
        "field_level": "等級/階級",
        "field_attribute": "屬性",
        "field_category": "效果分類",
    },
    "en": {
        "field_id": "Code",
        "field_type": "Card type",
        "field_alias": "Alias",
        "field_level": "Level/Rank",
        "field_attribute": "Attribute",
        "field_category": "Category",
    },
}


class HtmlPasteDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, strings: dict[str, str] | None = None) -> None:
        super().__init__(parent)
        self.strings = strings or STRINGS["zh_TW"]
        self.setWindowTitle(self.strings["paste_dialog_title"])
        self.resize(920, 720)

        layout = QVBoxLayout(self)
        self.title_label = QLabel(self.strings["paste_dialog_label"])
        self.title_label.setObjectName("dialogTitle")
        layout.addWidget(self.title_label)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText(self.strings["paste_dialog_placeholder"])
        layout.addWidget(self.editor)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.cancel_button = QPushButton(self.strings["cancel"])
        self.ok_button = QPushButton(self.strings["apply"])
        self.ok_button.setObjectName("primaryButton")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.accept)
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.ok_button)
        layout.addLayout(button_row)

    def get_html(self) -> str:
        return self.editor.toPlainText()


class SecondaryCompareDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        primary_repository: CardRepository,
        repository: CardRepository,
        current_card: CardRecord | None,
        html_service: HtmlService,
        strings: dict[str, str],
    ) -> None:
        super().__init__(parent)
        self.primary_repository = primary_repository
        self.repository = repository
        self.current_card = current_card
        self.html_service = html_service
        self.strings = strings
        self.filtered_cards: list[CardRecord] = []
        self.diff_rows: list[tuple[str, CardRecord, CardRecord | None]] = []
        self._selected_card: CardRecord | None = None
        self.batch_backup_path: Path | None = None
        self.batch_overwrite_count = 0

        self.setWindowTitle(strings["compare_window_title"])
        self.resize(1120, 760)

        root = QVBoxLayout(self)
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel(strings["compare_search"]))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(strings["compare_search_placeholder"])
        self.search_edit.textChanged.connect(self._refresh_list)
        search_row.addWidget(self.search_edit, 1)
        search_row.addWidget(QLabel(self._text("compare_filter", "差異篩選")))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem(self._text("compare_filter_all", "全部"), "all")
        self.filter_combo.addItem(self._text("compare_filter_different", "不同"), "different")
        self.filter_combo.addItem(self._text("compare_filter_missing", "主資料庫缺少"), "missing")
        self.filter_combo.addItem(self._text("compare_filter_same", "相同"), "same")
        self.filter_combo.currentIndexChanged.connect(self._refresh_list)
        search_row.addWidget(self.filter_combo)
        root.addLayout(search_row)

        content = QSplitter(Qt.Orientation.Horizontal)
        self.card_list = QListWidget()
        self.card_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.card_list.currentRowChanged.connect(self._update_compare)
        content.addWidget(self.card_list)

        compare_panel = QWidget()
        compare_layout = QVBoxLayout(compare_panel)
        compare_layout.setContentsMargins(0, 0, 0, 0)
        compare_layout.setSpacing(8)
        self.current_card_label = QLabel(strings["field_current_card"])
        self.current_card_view = QTextEdit()
        self.current_card_view.setReadOnly(True)
        self.selected_card_label = QLabel(strings["field_secondary_card"])
        self.selected_card_view = QTextEdit()
        self.selected_card_view.setReadOnly(True)
        compare_layout.addWidget(self.current_card_label)
        compare_layout.addWidget(self.current_card_view, 1)
        compare_layout.addWidget(self.selected_card_label)
        compare_layout.addWidget(self.selected_card_view, 1)
        content.addWidget(compare_panel)
        content.setSizes([360, 760])
        root.addWidget(content, 1)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.cancel_button = QPushButton(strings["close"])
        self.apply_button = QPushButton(strings["compare_load_to_editor"])
        self.overwrite_selected_button = QPushButton(self._text("compare_overwrite_selected", "覆蓋選取"))
        self.overwrite_filtered_button = QPushButton(self._text("compare_overwrite_filtered", "覆蓋篩選結果"))
        self.apply_button.setObjectName("primaryButton")
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        self.overwrite_selected_button.clicked.connect(self._overwrite_selected)
        self.overwrite_filtered_button.clicked.connect(self._overwrite_filtered)
        button_row.addWidget(self.overwrite_selected_button)
        button_row.addWidget(self.overwrite_filtered_button)
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        root.addLayout(button_row)

        self.current_card_view.setPlainText(self._format_card_text(current_card))
        self._refresh_list()
        if current_card is not None:
            for index, card in enumerate(self.filtered_cards):
                if card.card_id == current_card.card_id:
                    self.card_list.setCurrentRow(index)
                    break
        elif self.filtered_cards:
            self.card_list.setCurrentRow(0)

    def _text(self, key: str, fallback: str) -> str:
        return self.strings.get(key, fallback)

    def _status_for_card(self, secondary_card: CardRecord) -> tuple[str, CardRecord | None]:
        primary_card = self.primary_repository.get_card_by_id(secondary_card.card_id)
        if primary_card is None:
            return "missing", None
        return ("same" if primary_card == secondary_card else "different"), primary_card

    def _status_label(self, status: str) -> str:
        labels = {
            "missing": self._text("compare_filter_missing", "主資料庫缺少"),
            "different": self._text("compare_filter_different", "不同"),
            "same": self._text("compare_filter_same", "相同"),
        }
        return labels.get(status, status)

    def _refresh_list(self) -> None:
        keyword = self.search_edit.text().strip()
        filter_value = self.filter_combo.currentData() or "all"
        searched_cards = self.repository.search(keyword)
        self.diff_rows = []
        for card in searched_cards:
            status, primary_card = self._status_for_card(card)
            if filter_value != "all" and status != filter_value:
                continue
            self.diff_rows.append((status, card, primary_card))

        self.filtered_cards = [card for _status, card, _primary_card in self.diff_rows]
        self.card_list.clear()
        for status, card, _primary_card in self.diff_rows[:1000]:
            self.card_list.addItem(
                f"[{self._status_label(status)}] {card.card_id}  {self.html_service.format_card_name(card.name)}"
            )
        if self.diff_rows and self.card_list.currentRow() < 0:
            self.card_list.setCurrentRow(0)

    def _update_compare(self, index: int) -> None:
        if index < 0 or index >= len(self.diff_rows):
            self._selected_card = None
            self.selected_card_view.clear()
            return
        _status, self._selected_card, primary_card = self.diff_rows[index]
        self.current_card_view.setPlainText(self._format_card_text(primary_card))
        self.selected_card_view.setPlainText(self._format_card_text(self._selected_card))

    def _format_card_text(self, card: CardRecord | None) -> str:
        if card is None:
            return "-"
        return "\n".join(
            [
                f"id: {card.card_id}",
                self.html_service.format_card_name(card.name),
                f"setcode: {card.setcode}",
                f"type: {card.type_value}",
                f"race: {card.race}",
                f"attribute: {card.attribute}",
                f"atk/def: {card.atk}/{card.defense}",
                f"level: {card.level}",
                "",
                card.desc,
            ]
        ).strip()

    def selected_card(self) -> CardRecord | None:
        return self._selected_card

    def _selected_secondary_cards(self) -> list[CardRecord]:
        cards: list[CardRecord] = []
        for item in self.card_list.selectedItems():
            row = self.card_list.row(item)
            if 0 <= row < len(self.diff_rows):
                cards.append(self.diff_rows[row][1])
        return cards

    def _overwrite_cards(self, cards: list[CardRecord]) -> None:
        if not cards:
            return
        backup_path = self.primary_repository.upsert_cards(cards)
        self.batch_backup_path = backup_path
        self.batch_overwrite_count = len(cards)
        QMessageBox.information(
            self,
            self._text("compare_overwrite_selected", "覆蓋選取"),
            self._text("compare_batch_done", "已覆蓋 {count} 張卡，備份：{backup}").format(
                count=len(cards),
                backup=backup_path.name,
            ),
        )
        self.primary_repository.load()
        self._refresh_list()

    def _overwrite_selected(self) -> None:
        self._overwrite_cards(self._selected_secondary_cards())

    def _overwrite_filtered(self) -> None:
        self._overwrite_cards([card for _status, card, _primary_card in self.diff_rows])


class ScriptWorkshopDialog(QDialog):
    def __init__(self, parent: QWidget | None, strings: dict[str, str], script_path: Path, template_path: Path) -> None:
        super().__init__(parent)
        self.strings = strings
        self.script_path = script_path
        self.template_path = template_path

        self.setWindowTitle(strings["open_script_workshop"])
        self.resize(1100, 780)

        root = QVBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(strings["script_placeholder"])
        root.addWidget(self.editor, 1)

        button_row = QHBoxLayout()
        self.reload_button = QPushButton(strings["reload_script"])
        self.template_button = QPushButton(strings["load_single_template"])
        self.save_button = QPushButton(strings["save_script"])
        self.close_button = QPushButton(strings["close"])
        self.save_button.setObjectName("primaryButton")
        self.reload_button.clicked.connect(self.reload_script)
        self.template_button.clicked.connect(self.load_template)
        self.save_button.clicked.connect(self.save_script)
        self.close_button.clicked.connect(self.accept)
        button_row.addWidget(self.reload_button)
        button_row.addWidget(self.template_button)
        button_row.addWidget(self.save_button)
        button_row.addStretch(1)
        button_row.addWidget(self.close_button)
        root.addLayout(button_row)

        self.reload_script()

    def reload_script(self) -> None:
        if self.script_path.exists():
            self.editor.setPlainText(self.script_path.read_text(encoding="utf-8"))
        else:
            self.editor.clear()

    def load_template(self) -> None:
        if self.template_path.exists():
            self.editor.setPlainText(self.template_path.read_text(encoding="utf-8"))

    def save_script(self) -> None:
        self.script_path.parent.mkdir(parents=True, exist_ok=True)
        self.script_path.write_text(self.editor.toPlainText(), encoding="utf-8")


class ExtraTextsDialog(QDialog):
    def __init__(self, parent: QWidget | None, strings: dict[str, str], values: list[str]) -> None:
        super().__init__(parent)
        self.strings = strings
        self.setWindowTitle(strings["extra_texts"])
        self.resize(880, 560)

        self.editors: list[QLineEdit] = []
        root = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        for index in range(16):
            row = index // 2
            column = (index % 2) * 2
            label = QLabel(f"str{index + 1}")
            editor = QLineEdit()
            editor.setText(values[index] if index < len(values) else "")
            self.editors.append(editor)
            grid.addWidget(label, row, column)
            grid.addWidget(editor, row, column + 1)

        root.addLayout(grid)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        self.cancel_button = QPushButton(strings["cancel"])
        self.apply_button = QPushButton(strings["apply"])
        self.apply_button.setObjectName("primaryButton")
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.apply_button)
        root.addLayout(button_row)

    def values(self) -> list[str]:
        return [editor.text().strip() for editor in self.editors]


class BitmaskEditorDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        title: str,
        labels: dict[int, dict[str, str]],
        language: str,
        value: int,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 520)
        self.checkboxes: list[tuple[int, QCheckBox]] = []

        root = QVBoxLayout(self)
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)
        for index, (flag, names) in enumerate(labels.items()):
            checkbox = QCheckBox(f"{names.get(language) or names['en']} | {flag}")
            checkbox.setChecked((value & flag) == flag)
            self.checkboxes.append((flag, checkbox))
            grid.addWidget(checkbox, index // 2, index % 2)
        root.addLayout(grid)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Cancel" if language == "en" else "取消")
        apply_button = QPushButton("Apply" if language == "en" else "套用")
        apply_button.setObjectName("primaryButton")
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.accept)
        button_row.addWidget(cancel_button)
        button_row.addWidget(apply_button)
        root.addLayout(button_row)

    def value(self) -> int:
        result = 0
        for flag, checkbox in self.checkboxes:
            if checkbox.isChecked():
                result |= flag
        return result


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.project_root = Path(__file__).resolve().parent.parent
        self.settings_service = SettingsService(self.project_root / "settings.json")
        self.html_service = HtmlService()
        self.setcode_service = SetcodeService(self.project_root / "data")
        self.script_template_path = self.project_root / "data" / "single.lua"

        self.settings = self._default_settings()
        self.current_language = self.settings.language
        self.card_repository: CardRepository | None = None
        self.secondary_card_repository: CardRepository | None = None
        self.image_indexer: ImageIndexer | None = None
        self.filtered_cards: list[CardRecord] = []
        self.current_card: CardRecord | None = None
        self.current_card_original_id: int | None = None
        self.extra_text_editors: list[QLineEdit] = []
        self.option_combos: dict[str, QComboBox] = {}
        self.field_labels: dict[str, QLabel] = {}
        self._setcode_search_results_cache: list[tuple[int, str]] = []
        self._syncing_level_fields = False

        self._apply_initial_window_size()
        self._build_ui()
        self._build_menu()
        self._load_settings()
        self._apply_theme()
        self.retranslate_ui()
        self.reload_all_sources()

    def tr(self, key: str, **kwargs: object) -> str:
        text = STRINGS[self.current_language][key]
        return text.format(**kwargs)

    def _apply_initial_window_size(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(1320, 760)
            return
        available = screen.availableGeometry()
        width = min(1440, max(1180, available.width() - 90))
        height = min(800, max(680, available.height() - 170))
        self.resize(width, height)

    def _default_settings(self) -> AppSettings:
        return AppSettings(
            cdb_path="",
            secondary_cdb_path="",
            pics_path="",
            template_path="",
            output_path=str(self.project_root / "output.html"),
            language="zh_TW",
        )

    def _build_ui(self) -> None:
        root = QWidget(self)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        self.source_status_panel = self._build_source_status_panel()
        root_layout.addWidget(self.source_status_panel)

        self.html_tools_panel = self._build_html_tools_panel()
        root_layout.addWidget(self.html_tools_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_search_panel())
        splitter.addWidget(self._build_card_panel())
        splitter.addWidget(self._build_cdb_editor_panel())
        splitter.setSizes([270, 340, 760])
        root_layout.addWidget(splitter, 1)

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
            #sourceStatusPath, #helperText {
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
            #collapseButton {
                background: transparent;
                color: #2859c5;
                border: none;
                font-size: 15px;
                font-weight: 700;
                padding: 0;
                text-align: left;
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

        self.source_title_label = QLabel()
        self.source_title_label.setObjectName("sectionTitle")
        layout.addWidget(self.source_title_label)

        cdb_row = QHBoxLayout()
        self.cdb_label = QLabel("cards.cdb")
        self.cdb_status_label = QLabel()
        self.cdb_path_label = QLabel()
        self.cdb_path_label.setObjectName("sourceStatusPath")
        self.cdb_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        cdb_row.addWidget(self.cdb_label)
        cdb_row.addWidget(self.cdb_status_label)
        cdb_row.addWidget(self.cdb_path_label, 1)
        layout.addLayout(cdb_row)

        secondary_cdb_row = QHBoxLayout()
        self.secondary_cdb_label = QLabel("cards.cdb (2)")
        self.secondary_cdb_status_label = QLabel()
        self.secondary_cdb_path_label = QLabel()
        self.secondary_cdb_path_label.setObjectName("sourceStatusPath")
        self.secondary_cdb_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        secondary_cdb_row.addWidget(self.secondary_cdb_label)
        secondary_cdb_row.addWidget(self.secondary_cdb_status_label)
        secondary_cdb_row.addWidget(self.secondary_cdb_path_label, 1)
        layout.addLayout(secondary_cdb_row)

        pics_row = QHBoxLayout()
        self.pics_label = QLabel("pics/")
        self.pics_status_label = QLabel()
        self.pics_path_label = QLabel()
        self.pics_path_label.setObjectName("sourceStatusPath")
        self.pics_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        pics_row.addWidget(self.pics_label)
        pics_row.addWidget(self.pics_status_label)
        pics_row.addWidget(self.pics_path_label, 1)
        layout.addLayout(pics_row)
        return panel

    def _build_html_tools_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        outer_layout = QVBoxLayout(panel)
        outer_layout.setContentsMargins(14, 12, 14, 12)
        outer_layout.setSpacing(10)

        header_row = QHBoxLayout()
        self.html_toggle_button = QToolButton()
        self.html_toggle_button.setObjectName("collapseButton")
        self.html_toggle_button.setCheckable(True)
        self.html_toggle_button.setChecked(False)
        self.html_toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.html_toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.html_toggle_button.toggled.connect(self._toggle_html_tools)
        header_row.addWidget(self.html_toggle_button)
        header_row.addStretch(1)
        outer_layout.addLayout(header_row)

        self.html_tools_body = QWidget()
        body_layout = QVBoxLayout(self.html_tools_body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)

        action_row = QHBoxLayout()
        self.import_button = QPushButton()
        self.import_button.clicked.connect(self.import_html_draft)
        self.copy_export_button = QPushButton()
        self.copy_export_button.setObjectName("primaryButton")
        self.copy_export_button.clicked.connect(self.copy_export_html)
        action_row.addWidget(self.import_button)
        action_row.addWidget(self.copy_export_button)
        action_row.addStretch(1)
        body_layout.addLayout(action_row)

        toolbar_row = QHBoxLayout()
        self.bold_button = QPushButton("B")
        self.bold_button.setObjectName("toolbarButton")
        self.italic_button = QPushButton("I")
        self.italic_button.setObjectName("toolbarButton")
        self.underline_button = QPushButton("U")
        self.underline_button.setObjectName("toolbarButton")
        self.bold_button.clicked.connect(self.toggle_bold)
        self.italic_button.clicked.connect(self.toggle_italic)
        self.underline_button.clicked.connect(self.toggle_underline)
        toolbar_row.addWidget(self.bold_button)
        toolbar_row.addWidget(self.italic_button)
        toolbar_row.addWidget(self.underline_button)

        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self.apply_preset_font_size)
        toolbar_row.addWidget(self.size_combo)

        self.color_buttons: list[QPushButton] = []
        for color in self.html_service.PRESET_COLORS:
            color_button = QPushButton()
            color_button.setFixedSize(28, 28)
            color_button.setStyleSheet(
                f"background-color: {color}; border: 1px solid #bdbdbd; border-radius: 8px;"
            )
            color_button.clicked.connect(lambda _checked=False, value=color: self.apply_text_color(value))
            self.color_buttons.append(color_button)
            toolbar_row.addWidget(color_button)

        self.clear_format_button = QPushButton()
        self.clear_format_button.clicked.connect(self.clear_current_format)
        toolbar_row.addWidget(self.clear_format_button)
        toolbar_row.addStretch(1)
        body_layout.addLayout(toolbar_row)

        self.html_editor = QTextEdit()
        self.html_editor.setAcceptRichText(True)
        self.html_editor.setMinimumHeight(220)
        body_layout.addWidget(self.html_editor)

        self.html_tools_body.setVisible(False)
        outer_layout.addWidget(self.html_tools_body)
        return panel

    def _build_search_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.search_title_label = QLabel()
        self.search_title_label.setObjectName("sectionTitle")
        layout.addWidget(self.search_title_label)

        search_row = QHBoxLayout()
        self.search_keyword_label = QLabel()
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self._refresh_card_list)
        search_row.addWidget(self.search_keyword_label)
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
        self.card_image_preview.setMinimumSize(220, 320)
        self.card_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_image_preview.setStyleSheet("background:#fbfcff; border:1px solid #d5deed; border-radius:12px;")
        layout.addWidget(self.card_image_preview, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.effect_preview = QTextEdit()
        self.effect_preview.setReadOnly(True)
        self.effect_preview.setMinimumHeight(180)
        layout.addWidget(self.effect_preview, 1)

        self.copy_card_button = QPushButton()
        self.copy_card_button.setObjectName("primaryButton")
        self.copy_card_button.clicked.connect(self.copy_card_block)
        layout.addWidget(self.copy_card_button)
        return panel

    def _create_option_combo(self, key: str) -> QComboBox:
        combo = QComboBox()
        combo.setEditable(True)
        self.option_combos[key] = combo
        return combo

    def _build_cdb_editor_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panelCard")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.editor_title_label = QLabel()
        self.editor_title_label.setObjectName("sectionTitle")
        layout.addWidget(self.editor_title_label)

        self.edit_card_desc = QTextEdit()
        self.edit_card_desc.setMinimumHeight(76)
        layout.addWidget(self.edit_card_desc)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        self.edit_card_id = QLineEdit()
        self.edit_card_name = QLineEdit()
        self.edit_alias = QLineEdit()
        self.edit_setcode = QLineEdit()
        self.edit_level = QLineEdit()
        self.edit_atk = QLineEdit()
        self.edit_defense = QLineEdit()
        self.edit_card_id.textChanged.connect(self._update_script_path_label)
        self.edit_setcode.textChanged.connect(self._update_setcode_helper_label)
        self.edit_level.textChanged.connect(self._sync_level_split_from_raw)

        self.edit_ot = self._create_option_combo("ot")
        self.edit_type_value = self._create_option_combo("type")
        self.edit_race = self._create_option_combo("race")
        self.edit_attribute = self._create_option_combo("attribute")
        self.edit_category = self._create_option_combo("category")
        self.edit_category.currentTextChanged.connect(lambda _text: self._update_category_summary())

        self.field_widgets = {
            "field_id": self.edit_card_id,
            "field_name": self.edit_card_name,
            "field_ot": self.edit_ot,
            "field_type": self.edit_type_value,
            "field_alias": self.edit_alias,
            "field_setcode": self.edit_setcode,
            "field_atk": self.edit_atk,
            "field_def": self.edit_defense,
            "field_level": self.edit_level,
            "field_race": self.edit_race,
            "field_attribute": self.edit_attribute,
        }

        ordered_fields = list(self.field_widgets.items())
        for index, (key, widget) in enumerate(ordered_fields):
            label = QLabel()
            self.field_labels[key] = label
            row = index // 2
            column = (index % 2) * 2
            grid.addWidget(label, row, column)
            grid.addWidget(widget, row, column + 1)

        self.category_label = QLabel()
        self.category_flags_button = QPushButton()
        self.category_flags_button.clicked.connect(self._open_category_flags_dialog)
        self.category_summary_label = QLabel("-")
        self.category_summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        category_widget = QWidget()
        category_layout = QHBoxLayout(category_widget)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(6)
        category_layout.addWidget(self.category_flags_button)
        category_layout.addWidget(self.category_summary_label, 1)
        category_row = len(ordered_fields) // 2
        grid.addWidget(self.category_label, category_row, 2)
        grid.addWidget(category_widget, category_row, 3)

        layout.addLayout(grid)

        level_helper_row = QHBoxLayout()
        self.level_helper_label = QLabel("Level")
        self.level_main_edit = QLineEdit()
        self.level_main_edit.setMaximumWidth(56)
        self.level_lscale_label = QLabel("L")
        self.level_lscale_edit = QLineEdit()
        self.level_lscale_edit.setMaximumWidth(56)
        self.level_rscale_label = QLabel("R")
        self.level_rscale_edit = QLineEdit()
        self.level_rscale_edit.setMaximumWidth(56)
        self.level_main_edit.editingFinished.connect(self._sync_level_raw_from_split)
        self.level_lscale_edit.editingFinished.connect(self._sync_level_raw_from_split)
        self.level_rscale_edit.editingFinished.connect(self._sync_level_raw_from_split)
        level_helper_row.addWidget(self.level_helper_label)
        level_helper_row.addWidget(self.level_main_edit)
        level_helper_row.addWidget(self.level_lscale_label)
        level_helper_row.addWidget(self.level_lscale_edit)
        level_helper_row.addWidget(self.level_rscale_label)
        level_helper_row.addWidget(self.level_rscale_edit)
        level_helper_row.addStretch(1)
        layout.addLayout(level_helper_row)

        setcode_helper_row = QHBoxLayout()
        self.setcode_helper_title_label = QLabel()
        self.setcode_helper_title_label.setObjectName("helperText")
        self.setcode_helper_edit = QLineEdit()
        self.setcode_helper_edit.editingFinished.connect(self._sync_setcode_helper_to_numeric)
        self.setcode_search_combo = QComboBox()
        self.setcode_search_combo.setEditable(True)
        self.setcode_search_combo.setMinimumWidth(160)
        self.setcode_search_combo.setMaximumWidth(260)
        self.setcode_search_combo.activated.connect(self._add_selected_setcode_search_result)
        self.setcode_search_combo.lineEdit().returnPressed.connect(self._run_setcode_search)
        self.setcode_search_language_combo = QComboBox()
        self.setcode_search_language_combo.setMaximumWidth(110)
        self.setcode_search_language_combo.currentIndexChanged.connect(self._run_setcode_search)
        self.add_setcode_button = QPushButton("+")
        self.add_setcode_button.setFixedWidth(34)
        self.add_setcode_button.clicked.connect(self._run_setcode_search)
        setcode_helper_row.addWidget(self.setcode_helper_title_label)
        setcode_helper_row.addWidget(self.setcode_helper_edit, 1)
        setcode_helper_row.addWidget(self.setcode_search_language_combo)
        setcode_helper_row.addWidget(self.setcode_search_combo)
        setcode_helper_row.addWidget(self.add_setcode_button)
        layout.addLayout(setcode_helper_row)

        self.setcode_helper_label = QLabel()
        self.setcode_helper_label.setObjectName("helperText")
        self.setcode_helper_label.setWordWrap(True)
        self.setcode_helper_label.setVisible(False)

        search_apply_row = QHBoxLayout()
        self.extra_texts_button = QPushButton()
        self.extra_texts_button.clicked.connect(self._open_extra_texts_dialog)
        search_apply_row.addWidget(self.extra_texts_button)
        search_apply_row.addStretch(1)
        layout.addLayout(search_apply_row)

        self.extra_text_editors = [QLineEdit() for _ in range(16)]

        button_row = QHBoxLayout()
        self.load_button = QPushButton()
        self.save_button = QPushButton()
        self.save_button.setObjectName("primaryButton")
        self.reset_button = QPushButton()
        self.copy_secondary_button = QPushButton()
        self.open_script_workshop_button = QPushButton()
        self.add_button = QPushButton()
        self.delete_button = QPushButton()
        self.load_button.clicked.connect(self._load_selected_card_into_editor)
        self.save_button.clicked.connect(self._save_current_card_edits)
        self.reset_button.clicked.connect(self._reset_editor_to_current_card)
        self.copy_secondary_button.clicked.connect(self._load_from_secondary_cdb)
        self.open_script_workshop_button.clicked.connect(self._open_script_workshop)
        self.add_button.clicked.connect(self._add_new_card)
        self.delete_button.clicked.connect(self._delete_current_card)
        for button in (
            self.load_button,
            self.save_button,
            self.reset_button,
            self.copy_secondary_button,
            self.open_script_workshop_button,
            self.add_button,
            self.delete_button,
        ):
            button_row.addWidget(button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        return panel

    def _build_menu(self) -> None:
        self.file_menu = self.menuBar().addMenu("")
        self.edit_menu = self.menuBar().addMenu("")
        self.sources_menu = self.menuBar().addMenu("")
        self.language_menu = self.menuBar().addMenu("")

        self.import_html_action = QAction(self)
        self.import_html_action.triggered.connect(self.import_html_draft)
        self.copy_html_action = QAction(self)
        self.copy_html_action.triggered.connect(self.copy_export_html)
        self.file_menu.addAction(self.import_html_action)
        self.file_menu.addAction(self.copy_html_action)

        self.copy_card_action = QAction(self)
        self.copy_card_action.triggered.connect(self.copy_card_block)
        self.save_card_action = QAction(self)
        self.save_card_action.triggered.connect(self._save_current_card_edits)
        self.add_card_action = QAction(self)
        self.add_card_action.triggered.connect(self._add_new_card)
        self.delete_card_action = QAction(self)
        self.delete_card_action.triggered.connect(self._delete_current_card)
        self.edit_menu.addAction(self.copy_card_action)
        self.edit_menu.addAction(self.save_card_action)
        self.edit_menu.addAction(self.add_card_action)
        self.edit_menu.addAction(self.delete_card_action)

        self.pick_cdb_action = QAction(self)
        self.pick_cdb_action.triggered.connect(self._pick_cdb)
        self.pick_secondary_cdb_action = QAction(self)
        self.pick_secondary_cdb_action.triggered.connect(self._pick_secondary_cdb)
        self.pick_pics_action = QAction(self)
        self.pick_pics_action.triggered.connect(self._pick_pics)
        self.reload_sources_action = QAction(self)
        self.reload_sources_action.triggered.connect(self.reload_all_sources)
        self.sources_menu.addAction(self.pick_cdb_action)
        self.sources_menu.addAction(self.pick_secondary_cdb_action)
        self.sources_menu.addAction(self.pick_pics_action)
        self.sources_menu.addAction(self.reload_sources_action)

        self.language_actions: dict[str, QAction] = {}
        for language in LANGUAGES:
            action = QAction(self)
            action.triggered.connect(lambda _checked=False, lang=language: self._set_language(lang))
            self.language_menu.addAction(action)
            self.language_actions[language] = action

    def _load_settings(self) -> None:
        loaded = self.settings_service.load()
        defaults = self._default_settings()
        self.settings = AppSettings(
            cdb_path=loaded.cdb_path if loaded.cdb_path and Path(loaded.cdb_path).exists() else defaults.cdb_path,
            secondary_cdb_path=(
                loaded.secondary_cdb_path
                if loaded.secondary_cdb_path and Path(loaded.secondary_cdb_path).exists()
                else defaults.secondary_cdb_path
            ),
            pics_path=loaded.pics_path if loaded.pics_path and Path(loaded.pics_path).exists() else defaults.pics_path,
            template_path="",
            output_path=loaded.output_path or defaults.output_path,
            language=loaded.language if loaded.language in LANGUAGES else defaults.language,
        )
        self.current_language = self.settings.language

    def _save_settings(self) -> None:
        self.settings.language = self.current_language
        self.settings_service.save(self.settings)

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self.tr("window_title"))
        self.source_title_label.setText(self.tr("source_status"))
        self.cdb_label.setText("cards.cdb")
        self.secondary_cdb_label.setText("cards.cdb (2)")
        self.pics_label.setText("pics/")
        self.html_toggle_button.setText(self.tr("html_tools"))
        self.import_button.setText(self.tr("paste_html"))
        self.copy_export_button.setText(self.tr("copy_export_html"))
        self.clear_format_button.setText(self.tr("clear_format"))
        self.search_title_label.setText(self.tr("search_title"))
        self.search_keyword_label.setText(self.tr("search_keyword"))
        self.search_edit.setPlaceholderText(self.tr("search_placeholder"))
        self.copy_card_button.setText(self.tr("copy_card"))
        self.editor_title_label.setText(self.tr("cdb_editor"))
        self.edit_card_desc.setPlaceholderText(self.tr("effect_placeholder"))
        self.setcode_helper_title_label.setText(self.tr("field_setcode_text"))
        self.setcode_helper_edit.setPlaceholderText(self.tr("setcode_helper_placeholder"))
        self.setcode_search_combo.lineEdit().setPlaceholderText(self.tr("setcode_search_keyword"))
        self.setcode_search_language_combo.blockSignals(True)
        self.setcode_search_language_combo.clear()
        self.setcode_search_language_combo.addItem(self.tr("language_zh_TW"), "zh_TW")
        self.setcode_search_language_combo.addItem(self.tr("language_en"), "en")
        self.setcode_search_language_combo.addItem(self.tr("setcode_search_all"), "all")
        self.setcode_search_language_combo.blockSignals(False)
        self.add_setcode_button.setToolTip(self.tr("setcode_search_apply"))
        self.extra_texts_button.setText(self.tr("edit_extra_texts"))
        self.load_button.setText(self.tr("load_current"))
        self.save_button.setText(self.tr("save_changes"))
        self.reset_button.setText(self.tr("discard_changes"))
        self.copy_secondary_button.setText(self.tr("copy_from_secondary"))
        self.open_script_workshop_button.setText(self.tr("open_script_workshop"))
        self.add_button.setText(self.tr("add_card"))
        self.delete_button.setText(self.tr("delete_card"))
        self.category_label.setText(FIELD_LABEL_OVERRIDES.get(self.current_language, {}).get("field_category", self.tr("field_category")))
        self.category_flags_button.setText("Edit" if self.current_language == "en" else "編輯")
        self.level_helper_label.setText("Rank/Level" if self.current_language == "en" else "等級/階級")
        self.level_lscale_label.setText("L Scale" if self.current_language == "en" else "左刻度")
        self.level_rscale_label.setText("R Scale" if self.current_language == "en" else "右刻度")

        self.file_menu.setTitle(self.tr("menu_file"))
        self.edit_menu.setTitle(self.tr("menu_edit"))
        self.sources_menu.setTitle(self.tr("menu_sources"))
        self.language_menu.setTitle(self.tr("menu_language"))
        self.import_html_action.setText(self.tr("paste_html"))
        self.copy_html_action.setText(self.tr("copy_export_html"))
        self.copy_card_action.setText(self.tr("menu_copy_card"))
        self.save_card_action.setText(self.tr("menu_save_card"))
        self.add_card_action.setText(self.tr("add_card"))
        self.delete_card_action.setText(self.tr("delete_card"))
        self.pick_cdb_action.setText(self.tr("menu_pick_cdb"))
        self.pick_secondary_cdb_action.setText(self.tr("menu_pick_secondary_cdb"))
        self.pick_pics_action.setText(self.tr("menu_pick_pics"))
        self.reload_sources_action.setText(self.tr("menu_reload_sources"))
        self.language_actions["zh_TW"].setText(self.tr("language_zh_TW"))
        self.language_actions["en"].setText(self.tr("language_en"))

        self.size_combo.blockSignals(True)
        current_index = self.size_combo.currentIndex()
        self.size_combo.clear()
        self.size_combo.addItem(self.tr("size_placeholder"))
        self.size_combo.addItems(
            [
                self.tr("size_title"),
                self.tr("size_subtitle"),
                self.tr("size_normal"),
            ]
        )
        self.size_combo.setCurrentIndex(max(0, min(current_index, self.size_combo.count() - 1)))
        self.size_combo.blockSignals(False)
        self.html_editor.setPlaceholderText(self.tr("html_tools"))

        for key, label in self.field_labels.items():
            label.setText(FIELD_LABEL_OVERRIDES.get(self.current_language, {}).get(key, self.tr(key)))

        self._reload_option_combos()
        self._update_source_status_panel()
        self._update_setcode_helper_label()
        self._run_setcode_search()
        self._update_script_path_label()

    def _set_language(self, language: str) -> None:
        if language not in LANGUAGES or language == self.current_language:
            return
        self.current_language = language
        self.retranslate_ui()
        self._save_settings()

    def _reload_option_combos(self) -> None:
        for key, combo in self.option_combos.items():
            current_value = combo.currentText()
            numeric_value = current_value.split("|", 1)[-1].strip() if "|" in current_value else current_value.strip()
            combo.blockSignals(True)
            combo.clear()
            for value, labels in OPTION_LABELS[key].items():
                combo.addItem(f"{labels[self.current_language]} | {value}")
            if numeric_value:
                self._set_combo_value(combo, int(numeric_value))
            combo.blockSignals(False)

    def _set_source_status(
        self,
        status_label: QLabel,
        path_label: QLabel,
        is_ready: bool,
        path_value: str,
    ) -> None:
        status_label.setText(self.tr("selected") if is_ready else self.tr("not_selected"))
        status_label.setObjectName("sourceStatusValueReady" if is_ready else "sourceStatusValueMissing")
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)
        path_label.setText(path_value if path_value else self.tr("not_selected"))

    def _update_source_status_panel(self) -> None:
        cdb_path = self.settings.cdb_path.strip()
        secondary_cdb_path = self.settings.secondary_cdb_path.strip()
        pics_path = self.settings.pics_path.strip()
        has_cdb = bool(cdb_path and Path(cdb_path).exists())
        has_secondary_cdb = bool(secondary_cdb_path and Path(secondary_cdb_path).exists())
        has_pics = bool(pics_path and Path(pics_path).exists())
        self._set_source_status(self.cdb_status_label, self.cdb_path_label, has_cdb, cdb_path)
        self._set_source_status(
            self.secondary_cdb_status_label,
            self.secondary_cdb_path_label,
            has_secondary_cdb,
            secondary_cdb_path,
        )
        self._set_source_status(self.pics_status_label, self.pics_path_label, has_pics, pics_path)
        secondary_ok = (not secondary_cdb_path) or has_secondary_cdb
        self.source_status_panel.setVisible(not (has_cdb and has_pics and secondary_ok))

    def _toggle_html_tools(self, is_expanded: bool) -> None:
        self.html_toggle_button.setArrowType(Qt.ArrowType.DownArrow if is_expanded else Qt.ArrowType.RightArrow)
        self.html_tools_body.setVisible(is_expanded)

    def _toggle_extra_text_panel(self, is_expanded: bool) -> None:
        self.extra_text_toggle_button.setArrowType(Qt.ArrowType.DownArrow if is_expanded else Qt.ArrowType.RightArrow)
        self.extra_text_panel.setVisible(is_expanded)

    def _pick_cdb(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("pick_cdb_title"),
            self.settings.cdb_path,
            "CDB (*.cdb);;All Files (*)",
        )
        if file_path:
            self.settings.cdb_path = file_path
            self._save_settings()
            self.reload_all_sources()

    def _pick_secondary_cdb(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("pick_secondary_cdb_title"),
            self.settings.secondary_cdb_path,
            "CDB (*.cdb);;All Files (*)",
        )
        if file_path:
            self.settings.secondary_cdb_path = file_path
            self._save_settings()
            self.reload_all_sources()

    def _pick_pics(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("pick_pics_title"),
            self.settings.pics_path,
        )
        if directory:
            self.settings.pics_path = directory
            self._save_settings()
            self.reload_all_sources()

    def reload_all_sources(self) -> None:
        cdb_path = self.settings.cdb_path.strip()
        secondary_cdb_path = self.settings.secondary_cdb_path.strip()
        pics_path = self.settings.pics_path.strip()
        self._update_source_status_panel()

        if not cdb_path or not Path(cdb_path).exists():
            self.card_repository = None
            self.secondary_card_repository = None
            self.image_indexer = None
            self._show_no_data_state()
            self.statusBar().showMessage(self.tr("missing_cdb"), 5000)
            return

        try:
            self.card_repository = CardRepository(cdb_path)
            self.card_repository.load()
            if secondary_cdb_path and Path(secondary_cdb_path).exists():
                self.secondary_card_repository = CardRepository(secondary_cdb_path)
                self.secondary_card_repository.load()
            else:
                self.secondary_card_repository = None
            if pics_path and Path(pics_path).exists():
                self.image_indexer = ImageIndexer(pics_path)
                self.image_indexer.build()
            else:
                self.image_indexer = None
            self._refresh_card_list()
            self.statusBar().showMessage(self.tr("loaded_sources"), 5000)
        except Exception as exc:
            self.card_repository = None
            self.secondary_card_repository = None
            self.image_indexer = None
            self._show_no_data_state()
            QMessageBox.critical(self, self.tr("load_failed"), str(exc))

    def import_html_draft(self) -> None:
        dialog = HtmlPasteDialog(self, STRINGS[self.current_language])
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        raw_html = dialog.get_html().strip()
        if not raw_html:
            return
        self.html_editor.setHtml(self.html_service.sanitize_pasted_html(raw_html))
        self.statusBar().showMessage(self.tr("loaded_html"), 5000)

    def _refresh_card_list(self) -> None:
        keyword = self.search_edit.text().strip()
        if self.card_repository is None:
            self._show_no_data_state()
            return
        self.filtered_cards = self.card_repository.search(keyword)
        self.card_list.setEnabled(True)
        self.card_list.clear()
        for card in self.filtered_cards[:500]:
            self.card_list.addItem(QListWidgetItem(self.html_service.format_card_name(card.name)))
        if self.filtered_cards:
            self.card_list.setCurrentRow(0)
        else:
            self._update_card_details(None)

    def _show_no_data_state(self) -> None:
        self.filtered_cards = []
        self.card_list.clear()
        self.card_list.addItem(self.tr("no_data"))
        self.card_list.setEnabled(False)
        self.current_card = None
        self.current_card_original_id = None
        self.card_name_label.setText("-")
        self.card_image_id_label.setText("-")
        self.card_image_preview.clear()
        self.effect_preview.setPlainText(self.tr("no_data"))
        self._clear_cdb_editor()

    def _on_card_selected(self, index: int) -> None:
        if index < 0 or index >= len(self.filtered_cards):
            self._update_card_details(None)
            return
        self._update_card_details(self.filtered_cards[index])

    def _update_card_details(self, card: CardRecord | None) -> None:
        self.current_card = card
        self.current_card_original_id = card.card_id if card is not None else None
        if card is None:
            self.card_name_label.setText("-")
            self.card_image_id_label.setText("-")
            self.card_image_preview.clear()
            self.effect_preview.clear()
            self._clear_cdb_editor()
            return
        self.card_name_label.setText(self.html_service.format_card_name(card.name))
        self.card_image_id_label.setText(str(card.card_id))
        self.effect_preview.setPlainText(card.desc)
        self._fill_cdb_editor(card)
        image_path = self._get_card_image(card)
        if image_path and image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                self.card_image_preview.setPixmap(
                    pixmap.scaled(220, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
            QMessageBox.warning(self, self.tr("warn_no_card_title"), self.tr("warn_no_card_text"))
            return None
        return CardContext(card=card, local_image_path=self._get_card_image(card), public_image_url="", comment="")

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
        self.statusBar().showMessage(self.tr("copied_word"), 5000)

    def _option_text(self, key: str, value: int) -> str:
        labels = OPTION_LABELS[key].get(value)
        if labels is None:
            if key == "type":
                return f"{self._describe_flags(TYPE_FLAG_LABELS, value)} | {value}"
            if key == "category":
                return f"{self._describe_flags(CATEGORY_FLAG_LABELS, value)} | {value}"
            return str(value)
        return f"{labels[self.current_language]} | {value}"

    def _describe_flags(self, labels: dict[int, dict[str, str]], value: int) -> str:
        if value == 0:
            return "None" if self.current_language == "en" else "無"
        names = [
            label.get(self.current_language) or label["en"]
            for flag, label in labels.items()
            if value & flag
        ]
        return " + ".join(names) if names else str(value)

    def _set_combo_value(self, combo: QComboBox, value: int) -> None:
        combo.setEditText(self._option_text(self._combo_key(combo), value))

    def _combo_key(self, combo: QComboBox) -> str:
        for key, current_combo in self.option_combos.items():
            if current_combo is combo:
                return key
        raise KeyError("Unknown combo")

    def _read_combo_int(self, combo: QComboBox, field_name: str) -> int:
        raw = combo.currentText().strip()
        if not raw:
            raise ValueError(self.tr("field_required", name=field_name))
        return int(raw.split("|", 1)[-1].strip() if "|" in raw else raw)

    def _combo_int_or_zero(self, combo: QComboBox) -> int:
        raw = combo.currentText().strip()
        if not raw:
            return 0
        return int(raw.split("|", 1)[-1].strip() if "|" in raw else raw)

    def _open_category_flags_dialog(self) -> None:
        dialog = BitmaskEditorDialog(
            self,
            "Category Flags" if self.current_language == "en" else "category 多選",
            CATEGORY_FLAG_LABELS,
            self.current_language,
            self._combo_int_or_zero(self.edit_category),
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._set_combo_value(self.edit_category, dialog.value())
            self._update_category_summary()

    def _update_category_summary(self) -> None:
        try:
            value = self._combo_int_or_zero(self.edit_category)
        except ValueError:
            self.category_summary_label.setText(self.edit_category.currentText().strip() or "-")
            return
        self.category_summary_label.setText(f"{self._describe_flags(CATEGORY_FLAG_LABELS, value)} | {value}")

    def _parse_setcode_helper_text(self, raw: str) -> int:
        return self.setcode_service.parse_input(raw)

    def _format_setcode_chunks(self, setcode: int) -> str:
        descriptions = self.setcode_service.describe(setcode, self.current_language)
        if not descriptions:
            return self.tr("setcode_helper_empty")
        return ", ".join(descriptions)

    def _format_setcode_input_text(self, setcode: int) -> str:
        chunks = self.setcode_service.split_chunks(setcode)
        if not chunks:
            return ""
        return ", ".join(
            self.setcode_service.get_label(chunk, self.current_language) or f"0x{chunk:04X}"
            for chunk in chunks
        )

    def _update_setcode_helper_label(self) -> None:
        try:
            setcode_value = int(self.edit_setcode.text().strip() or "0")
        except ValueError:
            self.setcode_helper_label.setText(self.tr("setcode_helper_hint", text=self.edit_setcode.text().strip()))
            return
        helper_text = f"{self._format_setcode_chunks(setcode_value)} | hex: 0x{setcode_value:X}"
        self.setcode_helper_label.setText(self.tr("setcode_helper_hint", text=helper_text))

    def _current_setcode_search_language(self) -> str:
        language = self.setcode_search_language_combo.currentData()
        return str(language) if language else "all"

    def _run_setcode_search(self, *_args: object) -> None:
        keyword = self.setcode_search_combo.currentText().strip()
        language = self._current_setcode_search_language()
        self.setcode_search_combo.blockSignals(True)
        self.setcode_search_combo.clear()
        self.setcode_search_combo.setEditText(keyword)
        self.setcode_search_combo.blockSignals(False)
        self._setcode_search_results_cache = []
        if not keyword:
            return

        if language == "all":
            merged: dict[int, str] = {}
            for lang in LANGUAGES:
                for code, label in self.setcode_service.search(keyword, lang):
                    if code not in merged:
                        merged[code] = label
                    elif label and label not in merged[code]:
                        merged[code] = f"{merged[code]} / {label}"
            results = list(merged.items())
        else:
            results = self.setcode_service.search(keyword, language)

        self._setcode_search_results_cache = results
        self.setcode_search_combo.blockSignals(True)
        for code, label in results:
            self.setcode_search_combo.addItem(f"0x{code:04X} | {label}", code)
        self.setcode_search_combo.setEditText(keyword)
        self.setcode_search_combo.blockSignals(False)
        if results:
            self.setcode_search_combo.showPopup()

    def _add_selected_setcode_search_result(self, *_args: object) -> None:
        text = self.setcode_search_combo.currentText().strip()
        if "|" not in text:
            return
        code = self.setcode_search_combo.currentData()
        label = self.setcode_service.get_label(int(code), self.current_language) if code is not None else None
        if not label:
            label = text.split("|", 1)[1].strip()
        current = self.setcode_helper_edit.text().strip()
        self.setcode_helper_edit.setText(f"{current}, {label}" if current else label)
        self._sync_setcode_helper_to_numeric()

    def _open_extra_texts_dialog(self) -> None:
        dialog = ExtraTextsDialog(self, STRINGS[self.current_language], [editor.text() for editor in self.extra_text_editors])
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        values = dialog.values()
        for index, editor in enumerate(self.extra_text_editors):
            editor.setText(values[index] if index < len(values) else "")

    def _sync_setcode_helper_to_numeric(self) -> None:
        helper_text = self.setcode_helper_edit.text().strip()
        if not helper_text:
            self._update_setcode_helper_label()
            return
        try:
            setcode_value = self._parse_setcode_helper_text(helper_text)
        except ValueError as exc:
            QMessageBox.warning(self, self.tr("save_failed"), str(exc))
            return
        self.edit_setcode.setText(str(setcode_value))
        self._update_setcode_helper_label()

    def _sync_level_split_from_raw(self) -> None:
        if self._syncing_level_fields:
            return
        self._syncing_level_fields = True
        try:
            raw_level = int(self.edit_level.text().strip() or "0")
            level_value = raw_level & 0xFF
            right_scale = (raw_level >> 16) & 0xFF
            left_scale = (raw_level >> 24) & 0xFF
            self.level_main_edit.setText(str(level_value))
            self.level_lscale_edit.setText(str(left_scale))
            self.level_rscale_edit.setText(str(right_scale))
        except ValueError:
            self.level_main_edit.clear()
            self.level_lscale_edit.clear()
            self.level_rscale_edit.clear()
        finally:
            self._syncing_level_fields = False

    def _sync_level_raw_from_split(self) -> None:
        if self._syncing_level_fields:
            return
        self._syncing_level_fields = True
        try:
            level_value = int(self.level_main_edit.text().strip() or "0") & 0xFF
            left_scale = int(self.level_lscale_edit.text().strip() or "0") & 0xFF
            right_scale = int(self.level_rscale_edit.text().strip() or "0") & 0xFF
            raw_level = level_value | (right_scale << 16) | (left_scale << 24)
            self.edit_level.setText(str(raw_level))
        finally:
            self._syncing_level_fields = False

    def _script_path_for_card_id(self, card_id: int) -> Path | None:
        cdb_path = self.settings.cdb_path.strip()
        if not cdb_path:
            return None
        return Path(cdb_path).resolve().parent / "script" / f"c{card_id}.lua"

    def _update_script_path_label(self) -> None:
        return

    def _open_script_workshop(self) -> None:
        try:
            card_id = self._read_int_field(self.edit_card_id, "field_id")
        except ValueError as exc:
            QMessageBox.warning(self, self.tr("save_failed"), str(exc))
            return
        script_path = self._script_path_for_card_id(card_id)
        if script_path is None:
            QMessageBox.warning(self, self.tr("save_failed"), self.tr("missing_cdb"))
            return
        dialog = ScriptWorkshopDialog(
            self,
            STRINGS[self.current_language],
            script_path,
            self.script_template_path,
        )
        dialog.exec()
        self._update_script_path_label()

    def _fill_cdb_editor(self, card: CardRecord) -> None:
        self.edit_card_id.setText(str(card.card_id))
        self.edit_card_name.setText(card.name)
        self.edit_card_desc.setPlainText(card.desc)
        self.edit_alias.setText(str(card.alias))
        self.edit_setcode.setText(str(card.setcode))
        self.setcode_helper_edit.setText(self._format_setcode_input_text(card.setcode))
        self.edit_level.setText(str(card.level))
        self.edit_atk.setText(str(card.atk))
        self.edit_defense.setText(str(card.defense))
        self._set_combo_value(self.edit_ot, card.ot)
        self._set_combo_value(self.edit_type_value, card.type_value)
        self._set_combo_value(self.edit_race, card.race)
        self._set_combo_value(self.edit_attribute, card.attribute)
        self._set_combo_value(self.edit_category, card.category)
        self._update_category_summary()
        self._sync_level_split_from_raw()
        extra_texts = (card.extra_texts + [""] * 16)[:16]
        for index, editor in enumerate(self.extra_text_editors):
            editor.setText(extra_texts[index])
        self._update_setcode_helper_label()
        self._update_script_path_label()

    def _clear_cdb_editor(self) -> None:
        for widget in (self.edit_card_id, self.edit_card_name, self.edit_alias, self.edit_setcode, self.edit_level, self.edit_atk, self.edit_defense):
            widget.clear()
        self.edit_card_desc.clear()
        self.setcode_helper_edit.clear()
        self.setcode_helper_label.clear()
        for combo in self.option_combos.values():
            combo.setEditText("")
        self.category_summary_label.setText("-")
        for editor in self.extra_text_editors:
            editor.clear()
        self.level_main_edit.clear()
        self.level_lscale_edit.clear()
        self.level_rscale_edit.clear()

    def _load_selected_card_into_editor(self) -> None:
        card = self._get_selected_card()
        if card is None:
            QMessageBox.warning(self, self.tr("warn_no_card_title"), self.tr("warn_no_card_text"))
            return
        self._fill_cdb_editor(card)
        self.statusBar().showMessage(self.tr("loaded_editor"), 5000)

    def _reset_editor_to_current_card(self) -> None:
        if self.current_card is None:
            self._clear_cdb_editor()
            return
        self._fill_cdb_editor(self.current_card)
        self.statusBar().showMessage(self.tr("reset_editor"), 5000)

    def _read_int_field(self, field: QLineEdit, field_name_key: str) -> int:
        raw = field.text().strip()
        if not raw:
            raise ValueError(self.tr("field_required", name=self.tr(field_name_key)))
        return int(raw)

    def _build_card_from_editor(self) -> CardRecord:
        helper_text = self.setcode_helper_edit.text().strip()
        setcode_value = (
            self._parse_setcode_helper_text(helper_text)
            if helper_text
            else self._read_int_field(self.edit_setcode, "field_setcode")
        )
        return CardRecord(
            card_id=self._read_int_field(self.edit_card_id, "field_id"),
            name=self.edit_card_name.text().strip(),
            desc=self.edit_card_desc.toPlainText().strip(),
            ot=self._read_combo_int(self.edit_ot, self.tr("field_ot")),
            alias=self._read_int_field(self.edit_alias, "field_alias"),
            setcode=setcode_value,
            type_value=self._read_combo_int(self.edit_type_value, self.tr("field_type")),
            atk=self._read_int_field(self.edit_atk, "field_atk"),
            defense=self._read_int_field(self.edit_defense, "field_def"),
            level=self._read_int_field(self.edit_level, "field_level"),
            race=self._read_combo_int(self.edit_race, self.tr("field_race")),
            attribute=self._read_combo_int(self.edit_attribute, self.tr("field_attribute")),
            category=self._read_combo_int(self.edit_category, self.tr("field_category")),
            extra_texts=[editor.text().strip() for editor in self.extra_text_editors],
        )

    def _reload_repository_and_keep_selection(self, card_id: int | None = None) -> None:
        if self.card_repository is None:
            return
        self.card_repository.load()
        if self.secondary_card_repository is not None:
            self.secondary_card_repository.load()
        self._refresh_card_list()
        if card_id is not None:
            for index, card in enumerate(self.filtered_cards):
                if card.card_id == card_id:
                    self.card_list.setCurrentRow(index)
                    return

    def _load_from_secondary_cdb(self) -> None:
        if self.card_repository is None:
            QMessageBox.warning(self, self.tr("warn_no_repo_title"), self.tr("warn_no_repo_text"))
            return
        if self.secondary_card_repository is None:
            QMessageBox.warning(self, self.tr("warn_no_secondary_title"), self.tr("warn_no_secondary_text"))
            return
        dialog = SecondaryCompareDialog(
            self,
            self.card_repository,
            self.secondary_card_repository,
            self.current_card,
            self.html_service,
            STRINGS[self.current_language],
        )
        result = dialog.exec()
        if dialog.batch_overwrite_count:
            self._reload_repository_and_keep_selection(self.current_card.card_id if self.current_card else None)
        if result != QDialog.DialogCode.Accepted:
            return
        card = dialog.selected_card()
        if card is None:
            QMessageBox.warning(
                self,
                self.tr("warn_secondary_not_found_title"),
                self.tr("warn_secondary_not_found_text"),
            )
            return
        self._fill_cdb_editor(card)
        self.statusBar().showMessage(self.tr("loaded_from_secondary"), 5000)

    def _save_current_card_edits(self) -> None:
        if self.card_repository is None or self.current_card_original_id is None:
            QMessageBox.warning(self, self.tr("warn_no_repo_title"), self.tr("warn_no_repo_text"))
            return
        try:
            updated_card = self._build_card_from_editor()
            if not updated_card.name:
                raise ValueError(self.tr("name_required"))
            backup_path = self.card_repository.update_card(self.current_card_original_id, updated_card)
            self._reload_repository_and_keep_selection(updated_card.card_id)
            self.statusBar().showMessage(self.tr("saved_card", name=backup_path.name), 7000)
        except Exception as exc:
            QMessageBox.critical(self, self.tr("save_failed"), str(exc))

    def _add_new_card(self) -> None:
        if self.card_repository is None:
            QMessageBox.warning(self, self.tr("warn_no_repo_title"), self.tr("warn_no_repo_text"))
            return
        try:
            new_card = self._build_card_from_editor()
            if not new_card.name:
                raise ValueError(self.tr("name_required"))
            backup_path = self.card_repository.add_card(new_card)
            self._reload_repository_and_keep_selection(new_card.card_id)
            self.statusBar().showMessage(self.tr("added_card", name=backup_path.name), 7000)
        except Exception as exc:
            QMessageBox.critical(self, self.tr("save_failed"), str(exc))

    def _delete_current_card(self) -> None:
        card = self._get_selected_card()
        if self.card_repository is None or card is None:
            QMessageBox.warning(self, self.tr("warn_no_repo_title"), self.tr("warn_no_repo_text"))
            return
        result = QMessageBox.question(
            self,
            self.tr("confirm_delete_title"),
            self.tr("confirm_delete_text", id=card.card_id, name=self.html_service.format_card_name(card.name)),
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        try:
            backup_path = self.card_repository.delete_card(card.card_id)
            self._reload_repository_and_keep_selection(None)
            self.statusBar().showMessage(self.tr("deleted_card", name=backup_path.name), 7000)
        except Exception as exc:
            QMessageBox.critical(self, self.tr("save_failed"), str(exc))

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
        if index <= 0 or index > len(self.html_service.PRESET_FONT_SIZES):
            return
        formatter = QTextCharFormat()
        formatter.setFontPointSize(self.html_service.PRESET_FONT_SIZES[index - 1])
        self.merge_format(formatter)

    def clear_current_format(self) -> None:
        formatter = QTextCharFormat()
        formatter.setFontWeight(400)
        formatter.setFontItalic(False)
        formatter.setFontUnderline(False)
        formatter.setForeground(QColor("#444444"))
        formatter.setFontPointSize(self.html_service.PRESET_FONT_SIZES[2])
        self.merge_format(formatter)

    def build_export_html(self) -> str:
        return self.html_service.export_editor_html(self.html_editor.toHtml())

    def copy_export_html(self) -> None:
        QApplication.clipboard().setText(self.build_export_html())
        self.statusBar().showMessage(self.tr("copied_html"), 5000)


def run() -> None:
    app = QApplication(sys.argv)
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    icon_path = base_path / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    window = MainWindow()
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    sys.exit(app.exec())
