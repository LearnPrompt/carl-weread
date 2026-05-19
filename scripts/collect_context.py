#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.config import load_config
from carl_weread.context import collect_context_for_config, collect_recent_context


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect compact context for carl-weread.")
    parser.add_argument("vault", nargs="?", type=Path, help="Obsidian vault or notes folder path")
    parser.add_argument("--config", type=Path, help="carl-weread config.toml")
    parser.add_argument("--brief", help="Current user brief for chat mode")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=1200)
    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
        items = collect_context_for_config(
            config,
            brief=args.brief,
            today=date.today(),
            days=args.days,
            max_chars_per_file=args.max_chars,
        )
    elif args.vault:
        items = collect_recent_context(args.vault, today=date.today(), days=args.days, max_chars_per_file=args.max_chars)
    else:
        parser.error("需要提供 vault 路径，或使用 --config 指定配置文件")

    for item in items:
        print(f"## {item.kind}: {item.source}\n{item.text}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
