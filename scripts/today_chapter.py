#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from carl_weread.today_chapter import Chapter, ContextItem, choose_today_chapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Choose today's reading chapter from context and candidate chapters JSON.")
    parser.add_argument("--context", required=True, type=Path, help="JSON list: {kind, source, text}")
    parser.add_argument("--chapters", required=True, type=Path, help="JSON list: {book_id, book_title, chapter_uid, title}")
    args = parser.parse_args()

    context_data = json.loads(args.context.read_text(encoding="utf-8"))
    chapter_data = json.loads(args.chapters.read_text(encoding="utf-8"))
    context = [ContextItem(**item) for item in context_data]
    chapters = [Chapter(**item) for item in chapter_data]
    rec = choose_today_chapter(context, chapters)
    print(json.dumps(rec.__dict__, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
