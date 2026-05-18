from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class ContextItem:
    kind: str
    source: str
    text: str


def _read_snippet(path: Path, max_chars: int) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")[:max_chars].strip()


def _recent_daily_paths(vault: Path, today: date, days: int) -> list[Path]:
    daily_dir = vault / "10_日记"
    return [daily_dir / f"{today - timedelta(days=offset):%Y-%m-%d}.md" for offset in range(days)]


def _first_markdown_files(root: Path, limit: int = 8) -> list[Path]:
    if not root.exists():
        return []
    return sorted((p for p in root.rglob("*.md") if p.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def collect_recent_context(
    vault_path: str | Path,
    today: date | None = None,
    days: int = 3,
    max_chars_per_file: int = 1200,
) -> list[ContextItem]:
    """Collect a compact context bundle from Obsidian daily/project/topic notes."""
    vault = Path(vault_path).expanduser()
    today = today or date.today()
    items: list[ContextItem] = []

    for path in _recent_daily_paths(vault, today, days):
        if path.exists():
            items.append(ContextItem("daily", str(path.relative_to(vault)), _read_snippet(path, max_chars_per_file)))

    for path in _first_markdown_files(vault / "20_项目", limit=6):
        items.append(ContextItem("project", str(path.relative_to(vault)), _read_snippet(path, max_chars_per_file)))

    for path in _first_markdown_files(vault / "15_自媒体" / "选题库", limit=6):
        items.append(ContextItem("topic", str(path.relative_to(vault)), _read_snippet(path, max_chars_per_file)))

    return [item for item in items if item.text]
