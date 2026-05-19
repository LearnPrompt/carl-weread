#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.config import ContextConfig, load_config
from carl_weread.digest_apply import ReadingInput, build_action_card
from carl_weread.writeback import write_action_card


def default_config_path() -> Path:
    return Path.home() / ".config" / "carl-weread" / "config.toml"


def _input_from_args(args: argparse.Namespace) -> ReadingInput:
    if args.input:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        return ReadingInput(**data)
    if not args.book_title or not args.chapter_title:
        raise ValueError("未提供 --input 时，必须提供 --book-title 和 --chapter-title")
    highlights = args.highlight or []
    if args.highlights_file:
        highlights.extend(
            line.strip()
            for line in args.highlights_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    return ReadingInput(
        book_title=args.book_title,
        chapter_title=args.chapter_title,
        highlights=highlights,
        current_problem=args.current_problem or "",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and optionally write back a reading action card.")
    parser.add_argument("--input", type=Path, help="JSON: book_title, chapter_title, highlights, current_problem")
    parser.add_argument("--book-title", help="Book title when not using --input")
    parser.add_argument("--chapter-title", help="Chapter title when not using --input")
    parser.add_argument("--highlight", action="append", help="Highlight/thought; can be passed multiple times")
    parser.add_argument("--highlights-file", type=Path, help="Plain text highlights, one per line")
    parser.add_argument("--current-problem", help="Current project/content problem this reading should answer")
    parser.add_argument("--output", type=Path, help="Optional explicit markdown output path")
    parser.add_argument("--writeback", action="store_true", help="Write to the configured Obsidian/folder target")
    parser.add_argument("--config", type=Path, default=default_config_path(), help="carl-weread config.toml")
    parser.add_argument("--writeback-dir", type=Path, help="Override writeback directory")
    args = parser.parse_args()

    try:
        reading = _input_from_args(args)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"输入失败：{exc}", file=sys.stderr)
        return 2

    card = build_action_card(reading)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(card + "\n", encoding="utf-8")
        print(f"已写入阅读行动卡：{args.output}")
        return 0

    if args.writeback:
        config = load_config(args.config) if args.config.exists() else ContextConfig(mode="chat")
        result = write_action_card(card, config, f"{reading.book_title}-{reading.chapter_title}", output_dir=args.writeback_dir)
        print(result.message)
        if result.path is None:
            print(card)
        return 0

    print(card)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
