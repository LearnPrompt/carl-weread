#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.candidates import build_candidate_chapters, chapters_to_jsonable, extract_book_refs, merge_book_refs


def _run_weread(weread_script: Path, args: list[str]) -> object:
    command = [str(weread_script), *args]
    if weread_script.suffix == ".py":
        command = [sys.executable, str(weread_script), *args]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch WeRead data and build today-compatible chapter candidates.")
    parser.add_argument("--weread-script", type=Path, default=Path("scripts/weread.sh"), help="Path to scripts/weread.sh")
    parser.add_argument("--output", required=True, type=Path, help="Output candidate chapters JSON")
    parser.add_argument("--limit-books", type=int, default=5, help="Maximum books to fetch chapter lists for")
    parser.add_argument("--notebooks-count", type=int, default=200, help="Notebook count passed to WeRead API")
    args = parser.parse_args()

    shelf_payload = _run_weread(args.weread_script, ["shelf"])
    notebooks_payload = _run_weread(args.weread_script, ["notebooks", f"--count={args.notebooks_count}"])
    book_refs = merge_book_refs(extract_book_refs(shelf_payload), extract_book_refs(notebooks_payload), limit=args.limit_books)

    chapterinfo_by_book_id = {}
    for ref in book_refs:
        chapterinfo_by_book_id[ref.book_id] = _run_weread(args.weread_script, ["chapters", f"--bookId={ref.book_id}"])

    candidates = build_candidate_chapters(shelf_payload, notebooks_payload, chapterinfo_by_book_id, limit_books=args.limit_books)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(chapters_to_jsonable(candidates), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已获取并写入候选章节：{args.output}（{len(candidates)} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
