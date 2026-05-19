#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.candidates import build_candidate_chapters, chapters_to_jsonable


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_chapterinfo_by_book_id(chapter_dir: Path) -> dict[str, object]:
    payloads: dict[str, object] = {}
    for path in sorted(chapter_dir.glob("*.json")):
        payloads[path.stem] = _read_json(path)
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser(description="Build today-compatible chapter candidates from WeRead API JSON files.")
    parser.add_argument("--shelf", required=True, type=Path, help="JSON output from scripts/weread.sh shelf")
    parser.add_argument("--notebooks", required=True, type=Path, help="JSON output from scripts/weread.sh notebooks")
    parser.add_argument("--chapter-dir", required=True, type=Path, help="Directory containing <bookId>.json chapterinfo files")
    parser.add_argument("--output", required=True, type=Path, help="Output candidate chapters JSON")
    parser.add_argument("--limit-books", type=int, help="Maximum books to include after merging shelf and notebooks")
    args = parser.parse_args()

    candidates = build_candidate_chapters(
        _read_json(args.shelf),
        _read_json(args.notebooks),
        _load_chapterinfo_by_book_id(args.chapter_dir),
        limit_books=args.limit_books,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(chapters_to_jsonable(candidates), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入候选章节：{args.output}（{len(candidates)} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
