#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.candidates import build_candidate_chapters, extract_book_refs, merge_book_refs
from carl_weread.config import load_config
from carl_weread.context import collect_context_for_config
from carl_weread.today_chapter import choose_today_chapter


def default_config_path() -> Path:
    return Path.home() / ".config" / "carl-weread" / "config.toml"


def _run_weread(weread_script: Path, args: list[str]) -> object:
    command = [str(weread_script), *args]
    if weread_script.suffix == ".py":
        command = [sys.executable, str(weread_script), *args]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=90)
    except subprocess.TimeoutExpired:
        print(f"WeRead命令超时：{' '.join(command[:2])} ...", file=sys.stderr)
        raise SystemExit(4)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return json.loads(result.stdout)


def _fetch_candidates(weread_script: Path, limit_books: int, notebooks_count: int):
    shelf_payload = _run_weread(weread_script, ["shelf"])
    notebooks_payload = _run_weread(weread_script, ["notebooks", f"--count={notebooks_count}"])
    book_refs = merge_book_refs(extract_book_refs(shelf_payload), extract_book_refs(notebooks_payload), limit=limit_books)
    chapterinfo_by_book_id = {
        ref.book_id: _run_weread(weread_script, ["chapters", f"--bookId={ref.book_id}"])
        for ref in book_refs
    }
    return build_candidate_chapters(shelf_payload, notebooks_payload, chapterinfo_by_book_id, limit_books=limit_books)


def _format_markdown(rec) -> str:
    return "\n".join(
        [
            "今天只读这一小节：",
            f"《{rec.book_title}》｜{rec.chapter_title}",
            "",
            "为什么是它：",
            rec.why,
            "",
            "读前问题：",
            rec.reading_question,
            "",
            "读完只做一个动作：",
            rec.apply_action,
            "",
            f"打开：{rec.deep_link}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch WeRead data and recommend today's chapter in one command.")
    parser.add_argument("--config", type=Path, default=default_config_path(), help="carl-weread config.toml")
    parser.add_argument("--brief", help="Current user brief for chat mode or extra context")
    parser.add_argument("--weread-script", type=Path, default=Path("scripts/weread.sh"), help="Path to scripts/weread.sh")
    parser.add_argument("--limit-books", type=int, default=5, help="Maximum books to fetch chapter lists for")
    parser.add_argument("--notebooks-count", type=int, default=200, help="Notebook count passed to WeRead API")
    args = parser.parse_args()

    config = load_config(args.config)
    context = collect_context_for_config(config, brief=args.brief)
    candidates = _fetch_candidates(args.weread_script, args.limit_books, args.notebooks_count)
    rec = choose_today_chapter(context, candidates)
    print(_format_markdown(rec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
