#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.config import load_config
from carl_weread.context import collect_context_for_config
from carl_weread.today_chapter import Chapter, choose_today_chapter


def _load_chapters(path: Path) -> list[Chapter]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Chapter(**item) for item in data]


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
    parser = argparse.ArgumentParser(description="Choose today's carl-weread chapter.")
    parser.add_argument("--config", required=True, type=Path, help="carl-weread config.toml")
    parser.add_argument("--chapters", required=True, type=Path, help="candidate chapters JSON")
    parser.add_argument("--brief", help="Current user brief for chat mode or extra context")
    args = parser.parse_args()

    config = load_config(args.config)
    context = collect_context_for_config(config, brief=args.brief)
    chapters = _load_chapters(args.chapters)
    rec = choose_today_chapter(context, chapters)
    print(_format_markdown(rec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
