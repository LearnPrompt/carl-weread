#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from carl_weread.weekly_loop import WeeklyReportInput, build_weekly_report, load_cards


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a weekly reading-action loop report.")
    parser.add_argument("--cards", nargs="*", type=Path, default=[], help="Markdown card files or directories")
    parser.add_argument("--context", default="", help="Optional weekly project/content context")
    parser.add_argument("--output", type=Path, help="Optional markdown output path")
    args = parser.parse_args()

    report = build_weekly_report(WeeklyReportInput(cards=load_cards(args.cards), context=args.context))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
