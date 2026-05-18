from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlencode


def seconds_to_readable(seconds: int) -> str:
    """Convert WeRead duration seconds to a Chinese human-readable string."""
    minutes = max(0, int(seconds)) // 60
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours} 小时 {mins} 分钟"
    if hours:
        return f"{hours} 小时"
    return f"{mins} 分钟"


def format_date(timestamp: int, tz: str = "Asia/Shanghai") -> str:
    """Format a Unix timestamp as YYYY-MM-DD in the requested timezone."""
    return datetime.fromtimestamp(int(timestamp), ZoneInfo(tz)).strftime("%Y-%m-%d")


def weread_link(book_id: str, chapter_uid: str | None = None) -> str:
    """Build a WeRead deep link for a book or a specific chapter."""
    params = {"bId": book_id}
    if chapter_uid:
        params["chapterUid"] = str(chapter_uid)
    return "weread://reading?" + urlencode(params)
