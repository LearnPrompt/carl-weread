from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .candidates import _unwrap_items


@dataclass(frozen=True)
class BookProfile:
    book_id: str
    title: str
    author: str = ""
    category: str = ""
    intro: str = ""
    source: str = "unknown"
    note_count: int = 0
    progress_percent: float | None = None


def _string_value(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _number_value(item: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = item.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _book_dict(raw_item: Any) -> dict[str, Any] | None:
    if not isinstance(raw_item, dict):
        return None
    for key in ("book", "bookInfo", "bookinfo", "info"):
        value = raw_item.get(key)
        if isinstance(value, dict):
            merged = dict(value)
            for outer_key in ("noteCount", "note_count", "readingTime", "progress", "progressPercent", "source"):
                if outer_key in raw_item and outer_key not in merged:
                    merged[outer_key] = raw_item[outer_key]
            return merged
    return raw_item


def extract_book_profiles(payload: Any, source: str = "unknown") -> list[BookProfile]:
    """Extract book profiles from common WeRead response shapes.

    The WeRead gateway returns slightly different envelopes across endpoints. This
    helper stays deliberately permissive so workflow code can reason about books
    without depending on one exact JSON shape.
    """
    raw_items = _unwrap_items(
        payload,
        (
            "books",
            "bookInfos",
            "bookInfo",
            "items",
            "records",
            "recommendBooks",
            "data",
            "bookProgress",
            "updated",
            "synckeys",
        ),
    )
    profiles: list[BookProfile] = []
    for raw_item in raw_items:
        item = _book_dict(raw_item)
        if item is None:
            continue
        book_id = _string_value(item, ("book_id", "bookId", "bookid", "id"))
        title = _string_value(item, ("book_title", "title", "bookName", "name"))
        if not book_id or not title:
            continue
        note_count = int(_number_value(item, ("noteCount", "note_count", "bookmarkCount", "reviewCount")) or 0)
        progress = _number_value(item, ("progressPercent", "progress", "percent", "readProgress"))
        profiles.append(
            BookProfile(
                book_id=book_id,
                title=title,
                author=_string_value(item, ("author", "authorName", "writer")),
                category=_string_value(item, ("category", "categoryName", "newCategory", "type")),
                intro=_string_value(item, ("intro", "brief", "description", "shortIntro")),
                source=source,
                note_count=note_count,
                progress_percent=progress,
            )
        )
    return profiles


def merge_profiles(*groups: list[BookProfile]) -> list[BookProfile]:
    merged: dict[str, BookProfile] = {}
    for group in groups:
        for profile in group:
            existing = merged.get(profile.book_id)
            if existing is None:
                merged[profile.book_id] = profile
                continue
            merged[profile.book_id] = BookProfile(
                book_id=existing.book_id,
                title=existing.title or profile.title,
                author=existing.author or profile.author,
                category=existing.category or profile.category,
                intro=existing.intro or profile.intro,
                source="/".join(dict.fromkeys([*existing.source.split("/"), *profile.source.split("/")])),
                note_count=max(existing.note_count, profile.note_count),
                progress_percent=existing.progress_percent if existing.progress_percent is not None else profile.progress_percent,
            )
    return list(merged.values())


def reading_evidence_ids(notebooks_payload: Any, progress_payloads: dict[str, Any] | None = None) -> set[str]:
    ids = {profile.book_id for profile in extract_book_profiles(notebooks_payload, source="notebooks") if profile.note_count > 0}
    for book_id, payload in (progress_payloads or {}).items():
        profiles = extract_book_profiles(payload, source="progress")
        if any((profile.progress_percent or 0) >= 20 for profile in profiles):
            ids.add(book_id)
    return ids
