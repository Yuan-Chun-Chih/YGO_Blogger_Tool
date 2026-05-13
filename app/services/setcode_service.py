from __future__ import annotations

from pathlib import Path


class SetcodeService:
    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.labels_by_language: dict[str, dict[int, str]] = {"zh_TW": {}, "en": {}}
        self.names_to_code: dict[str, int] = {}
        self.names_by_language: dict[str, dict[str, int]] = {"zh_TW": {}, "en": {}}
        self._load()

    def _load(self) -> None:
        self._load_language_file(self.data_dir / "cardinfo_chinese.txt", "zh_TW")
        self._load_language_file(self.data_dir / "cardinfo_english.txt", "en")

    def _load_language_file(self, path: Path, language: str) -> None:
        if not path.exists():
            return

        in_setname_section = False
        for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line == "##setname":
                in_setname_section = True
                continue
            if not in_setname_section:
                continue
            if line.startswith("#"):
                continue

            parts = [part.strip() for part in raw_line.split("\t")]
            if len(parts) < 2:
                continue

            try:
                code = int(parts[0], 0)
            except ValueError:
                continue

            candidates = [part for part in parts[1:] if part and part.upper() != "N/A"]
            if not candidates:
                continue

            label = candidates[0]
            self.labels_by_language[language][code] = label
            for candidate in candidates:
                normalized = candidate.casefold()
                self.names_to_code[normalized] = code
                self.names_by_language[language][normalized] = code

    def split_chunks(self, setcode: int) -> list[int]:
        if setcode <= 0:
            return []
        chunks: list[int] = []
        remaining = setcode
        while remaining > 0:
            chunks.append(remaining & 0xFFFF)
            remaining >>= 16
        return chunks

    def get_label(self, code: int, language: str) -> str | None:
        return self.labels_by_language.get(language, {}).get(code) or self.labels_by_language["en"].get(code)

    def describe(self, setcode: int, language: str) -> list[str]:
        descriptions: list[str] = []
        for code in self.split_chunks(setcode):
            label = self.get_label(code, language)
            if label:
                descriptions.append(f"0x{code:04X} {label}")
            else:
                descriptions.append(f"0x{code:04X}")
        return descriptions

    def parse_input(self, raw: str) -> int:
        normalized = raw.strip()
        if not normalized:
            return 0
        if "," not in normalized:
            return self._parse_token(normalized)

        parts = [part.strip() for part in normalized.split(",") if part.strip()]
        if not parts:
            return 0

        value = 0
        for index, part in enumerate(parts):
            chunk = self._parse_token(part)
            if chunk < 0 or chunk > 0xFFFF:
                raise ValueError("setcode chunk must be between 0x0000 and 0xFFFF.")
            value |= chunk << (index * 16)
        return value

    def _parse_token(self, token: str) -> int:
        try:
            return int(token, 0)
        except ValueError:
            pass

        code = self.names_to_code.get(token.casefold())
        if code is None:
            raise ValueError(f"Unknown setcode or archetype token: {token}")
        return code

    def search(self, keyword: str, language: str) -> list[tuple[int, str]]:
        normalized = keyword.strip().casefold()
        if not normalized:
            return []

        results: list[tuple[int, str]] = []
        mapping = self.names_by_language.get(language, {})
        for name, code in mapping.items():
            if normalized in name:
                label = self.get_label(code, language) or name
                results.append((code, label))

        seen: set[int] = set()
        deduped: list[tuple[int, str]] = []
        for code, label in results:
            if code in seen:
                continue
            seen.add(code)
            deduped.append((code, label))
        return deduped
