from __future__ import annotations

import re
from pathlib import Path


ENGLISH_NAMES = {
    "TYPE_MONSTER": "Monster",
    "TYPE_SPELL": "Spell",
    "TYPE_TRAP": "Trap",
    "TYPE_NORMAL": "Normal",
    "TYPE_EFFECT": "Effect",
    "TYPE_FUSION": "Fusion",
    "TYPE_RITUAL": "Ritual",
    "TYPE_TRAPMONSTER": "Trap Monster",
    "TYPE_SPIRIT": "Spirit",
    "TYPE_UNION": "Union",
    "TYPE_DUAL": "Gemini",
    "TYPE_TUNER": "Tuner",
    "TYPE_SYNCHRO": "Synchro",
    "TYPE_TOKEN": "Token",
    "TYPE_QUICKPLAY": "Quick-Play",
    "TYPE_CONTINUOUS": "Continuous",
    "TYPE_EQUIP": "Equip",
    "TYPE_FIELD": "Field",
    "TYPE_COUNTER": "Counter",
    "TYPE_FLIP": "Flip",
    "TYPE_TOON": "Toon",
    "TYPE_XYZ": "Xyz",
    "TYPE_PENDULUM": "Pendulum",
    "TYPE_SPSUMMON": "Special Summon",
    "TYPE_LINK": "Link",
    "ATTRIBUTE_EARTH": "Earth",
    "ATTRIBUTE_WATER": "Water",
    "ATTRIBUTE_FIRE": "Fire",
    "ATTRIBUTE_WIND": "Wind",
    "ATTRIBUTE_LIGHT": "Light",
    "ATTRIBUTE_DARK": "Dark",
    "ATTRIBUTE_DEVINE": "Divine",
    "RACE_WARRIOR": "Warrior",
    "RACE_SPELLCASTER": "Spellcaster",
    "RACE_FAIRY": "Fairy",
    "RACE_FIEND": "Fiend",
    "RACE_ZOMBIE": "Zombie",
    "RACE_MACHINE": "Machine",
    "RACE_AQUA": "Aqua",
    "RACE_PYRO": "Pyro",
    "RACE_ROCK": "Rock",
    "RACE_WINDBEAST": "Winged Beast",
    "RACE_PLANT": "Plant",
    "RACE_INSECT": "Insect",
    "RACE_THUNDER": "Thunder",
    "RACE_DRAGON": "Dragon",
    "RACE_BEAST": "Beast",
    "RACE_BEASTWARRIOR": "Beast-Warrior",
    "RACE_DINOSAUR": "Dinosaur",
    "RACE_FISH": "Fish",
    "RACE_SEASERPENT": "Sea Serpent",
    "RACE_REPTILE": "Reptile",
    "RACE_PSYCHO": "Psychic",
    "RACE_DEVINE": "Divine Beast",
    "RACE_CREATORGOD": "Creator God",
    "RACE_WYRM": "Wyrm",
    "RACE_CYBERSE": "Cyberse",
    "RACE_ILLUSION": "Illusion",
    "CATEGORY_DESTROY": "Destroy",
    "CATEGORY_RELEASE": "Release",
    "CATEGORY_REMOVE": "Banish",
    "CATEGORY_TOHAND": "To Hand",
    "CATEGORY_TODECK": "To Deck",
    "CATEGORY_TOGRAVE": "Send to Grave",
    "CATEGORY_DECKDES": "Deck to Grave",
    "CATEGORY_HANDES": "Discard",
    "CATEGORY_SUMMON": "Summon",
    "CATEGORY_SPECIAL_SUMMON": "Special Summon",
    "CATEGORY_TOKEN": "Token",
    "CATEGORY_FLIP": "Flip",
    "CATEGORY_POSITION": "Change Position",
    "CATEGORY_CONTROL": "Control",
    "CATEGORY_DISABLE": "Negate Effect",
    "CATEGORY_DISABLE_SUMMON": "Negate Summon",
    "CATEGORY_DRAW": "Draw",
    "CATEGORY_SEARCH": "Search",
    "CATEGORY_EQUIP": "Equip",
    "CATEGORY_DAMAGE": "Damage",
    "CATEGORY_RECOVER": "Recover",
    "CATEGORY_ATKCHANGE": "Change ATK",
    "CATEGORY_DEFCHANGE": "Change DEF",
    "CATEGORY_COUNTER": "Counter",
    "CATEGORY_COIN": "Coin",
    "CATEGORY_DICE": "Dice",
    "CATEGORY_LEAVE_GRAVE": "Leave Grave",
    "CATEGORY_LVCHANGE": "Change Level",
    "CATEGORY_NEGATE": "Negate Activation",
    "CATEGORY_ANNOUNCE": "Declare Card Name",
    "CATEGORY_FUSION_SUMMON": "Fusion Summon",
}


def _fallback_english_name(constant_name: str, prefix: str) -> str:
    raw = constant_name.removeprefix(prefix).replace("_", " ").lower()
    return raw.title()


def _read_constants(path: Path) -> dict[str, dict[int, dict[str, str]]]:
    groups: dict[str, dict[int, dict[str, str]]] = {
        "type": {},
        "attribute": {0: {"zh_TW": "無", "en": "None"}},
        "race": {},
        "category": {0: {"zh_TW": "無", "en": "None"}},
    }
    if not path.exists():
        return groups

    pattern = re.compile(r"^(TYPE|ATTRIBUTE|RACE|CATEGORY)_([A-Z0-9_]+)\s*=\s*(0x[0-9a-fA-F]+|\d+)(?:\s*--\s*(.*))?$")
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue

        prefix, _name, raw_value, comment = match.groups()
        key = prefix.lower()
        constant_name = f"{prefix}_{_name}"
        value = int(raw_value, 0)
        if key == "race" and constant_name == "RACE_ALL":
            continue

        zh_name = (comment or "").strip() or ENGLISH_NAMES.get(constant_name) or _fallback_english_name(constant_name, f"{prefix}_")
        en_name = ENGLISH_NAMES.get(constant_name) or _fallback_english_name(constant_name, f"{prefix}_")
        groups[key][value] = {"zh_TW": zh_name, "en": en_name}

    # Newer card pools may use constants absent from older constant.lua files.
    groups["type"].setdefault(67108864, {"zh_TW": "連結", "en": "Link"})
    groups["race"].setdefault(16777216, {"zh_TW": "電子界", "en": "Cyberse"})
    groups["race"].setdefault(33554432, {"zh_TW": "幻想魔", "en": "Illusion"})
    return groups


def load_constant_option_labels(data_dir: str | Path) -> dict[str, dict[int, dict[str, str]]]:
    return _read_constants(Path(data_dir) / "constant.lua")
