from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .today_chapter import Chapter


@dataclass(frozen=True)
class BookRef:
    book_id: str
    title: str


def _unwrap_items(payload: Any, keys: tuple[str, ...]) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []

    containers = [payload]
    for wrapper_key in ("data", "result"):
        wrapped = payload.get(wrapper_key)
        if isinstance(wrapped, dict):
            containers.append(wrapped)

    for container in containers:
        for key in keys:
            value = container.get(key)
            if isinstance(value, list):
                return value
    return []


def _string_value(item: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = item.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def extract_book_refs(payload: Any, limit: int | None = None) -> list[BookRef]:
    refs: list[BookRef] = []
    for raw_item in _unwrap_items(payload, ("books", "bookProgress", "updated", "synckeys")):
        if not isinstance(raw_item, dict):
            continue
        item = raw_item.get("book") if isinstance(raw_item.get("book"), dict) else raw_item
        book_id = _string_value(item, ("book_id", "bookId", "bookid", "id"))
        title = _string_value(item, ("book_title", "title", "bookName", "name"))
        if book_id and title:
            refs.append(BookRef(book_id=book_id, title=title))
        if limit is not None and len(refs) >= limit:
            break
    return refs


def chapters_from_chapterinfo(book_id: str, book_title: str, payload: Any) -> list[Chapter]:
    chapters: list[Chapter] = []
    for item in _unwrap_items(payload, ("chapters", "chapterInfos", "chapterInfo")):
        if not isinstance(item, dict):
            continue
        chapter_uid = _string_value(item, ("chapter_uid", "chapterUid", "uid", "chapterId", "id"))
        title = _string_value(item, ("title", "chapterName", "name"))
        if chapter_uid and title:
            chapters.append(Chapter(book_id=book_id, book_title=book_title, chapter_uid=chapter_uid, title=title))
    return chapters


def merge_book_refs(*groups: list[BookRef], limit: int | None = None) -> list[BookRef]:
    merged: list[BookRef] = []
    seen: set[str] = set()
    for group in groups:
        for ref in group:
            if ref.book_id in seen:
                continue
            seen.add(ref.book_id)
            merged.append(ref)
            if limit is not None and len(merged) >= limit:
                return merged
    return merged


def build_candidate_chapters(
    shelf_payload: Any,
    notebooks_payload: Any,
    chapterinfo_by_book_id: dict[str, Any],
    limit_books: int | None = None,
) -> list[Chapter]:
    book_refs = merge_book_refs(
        extract_book_refs(shelf_payload),
        extract_book_refs(notebooks_payload),
        limit=limit_books,
    )
    candidates: list[Chapter] = []
    for ref in book_refs:
        payload = chapterinfo_by_book_id.get(ref.book_id)
        if payload is None:
            continue
        candidates.extend(chapters_from_chapterinfo(ref.book_id, ref.title, payload))
    return candidates


def chapters_to_jsonable(chapters: list[Chapter]) -> list[dict[str, str]]:
    return [asdict(chapter) for chapter in chapters]
