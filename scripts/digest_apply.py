#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.digest_apply import ReadingInput, build_action_card


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an Obsidian-ready reading action card.")
    parser.add_argument("--input", required=True, type=Path, help="JSON: book_title, chapter_title, highlights, current_problem")
    parser.add_argument("--output", type=Path, help="Optional markdown output path")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    card = build_action_card(ReadingInput(**data))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(card + "\n", encoding="utf-8")
    else:
        print(card)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
