from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from .config import ContextConfig


@dataclass(frozen=True)
class WritebackResult:
    path: Path | None
    mode: str
    message: str


def slugify_title(title: str, max_length: int = 48) -> str:
    """Build a filesystem-safe, readable slug for Chinese/English titles."""
    cleaned = re.sub(r'[\\/:*?"<>|#\n\r\t]+', "-", title).strip(" -")
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned)
    return (cleaned or "reading-card")[:max_length].strip(" -") or "reading-card"


def default_writeback_dir(config: ContextConfig) -> Path | None:
    """Return the default directory for persisted action cards, if this mode writes files."""
    if config.mode == "obsidian" and config.path is not None:
        vault = Path(config.path).expanduser()
        preferred = vault / "15_自媒体" / "阅读行动卡"
        fallback = vault / "阅读行动卡"
        return preferred if preferred.parent.exists() else fallback
    if config.mode == "folder" and config.path is not None:
        return Path(config.path).expanduser() / "carl-weread" / "reading-cards"
    return None


def write_action_card(
    card_markdown: str,
    config: ContextConfig,
    title: str,
    output_dir: str | Path | None = None,
    today: date | None = None,
) -> WritebackResult:
    """Persist an action card when the configured mode has a real filesystem target.

    Chat and WeRead-only modes intentionally do not write files; the caller should return
    the markdown in conversation instead.
    """
    target_dir = Path(output_dir).expanduser() if output_dir is not None else default_writeback_dir(config)
    if target_dir is None:
        return WritebackResult(path=None, mode=config.mode, message="当前模式不写文件，已在对话中返回行动卡。")

    day = today or date.today()
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{day:%Y-%m-%d}-{slugify_title(title)}.md"
    path.write_text(card_markdown.rstrip() + "\n", encoding="utf-8")
    return WritebackResult(path=path, mode=config.mode, message=f"已写入阅读行动卡：{path}")
