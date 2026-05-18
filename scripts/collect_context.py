#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.context import collect_recent_context


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect compact Obsidian context for carl-weread.")
    parser.add_argument("vault", type=Path, help="Obsidian vault path")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=1200)
    args = parser.parse_args()

    items = collect_recent_context(args.vault, today=date.today(), days=args.days, max_chars_per_file=args.max_chars)
    for item in items:
        print(f"## {item.kind}: {item.source}\n{item.text}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
