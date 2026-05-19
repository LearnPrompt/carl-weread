from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from .after_read import AfterReadInput, build_after_read_result, extract_highlights
from .config import ContextConfig, load_config
from .context import collect_context_for_config
from .unread_advisor import format_unread_recommendation, recommend_unread_book
from .weekly_loop import WeeklyReportInput, build_weekly_report, load_cards
from .writeback import write_action_card


def default_config_path() -> Path:
    return Path.home() / ".config" / "carl-weread" / "config.toml"


def _load_config_or_chat(path: Path) -> ContextConfig:
    return load_config(path) if path.exists() else ContextConfig(mode="chat")


def _run_weread(weread_script: Path, args: list[str]) -> Any:
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


def _cmd_recommend(args: argparse.Namespace) -> int:
    config = _load_config_or_chat(args.config)
    context = collect_context_for_config(config, brief=args.brief)
    shelf_payload = _run_weread(args.weread_script, ["shelf"])
    notebooks_payload = _run_weread(args.weread_script, ["notebooks", f"--count={args.notebooks_count}"])
    recommendation_payloads = [_run_weread(args.weread_script, ["recommend", f"--count={args.count}"])]
    similar_payloads = []
    for book_id in args.similar_book_id or []:
        similar_payloads.append(_run_weread(args.weread_script, ["similar", f"--bookId={book_id}", f"--count={args.count}"]))
    search_payloads = []
    if args.keyword:
        search_payloads.append(_run_weread(args.weread_script, ["search", f"--keyword={args.keyword}"]))
    rec = recommend_unread_book(
        context=context,
        shelf_payload=shelf_payload,
        notebooks_payload=notebooks_payload,
        recommendation_payloads=recommendation_payloads,
        similar_payloads=similar_payloads,
        search_payloads=search_payloads,
        brief=args.brief or args.keyword or "",
    )
    if args.json:
        print(json.dumps(rec.__dict__, ensure_ascii=False, indent=2))
    else:
        print(format_unread_recommendation(rec))
    return 0


def _cmd_after_read(args: argparse.Namespace) -> int:
    highlights = list(args.highlight or [])
    if args.highlights_file:
        highlights.extend(
            line.strip()
            for line in args.highlights_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if args.auto_fetch:
        if not args.book_id or not args.chapter_uid:
            print("--auto-fetch 需要同时提供 --book-id 和 --chapter-uid", file=sys.stderr)
            return 2
        payload = _run_weread(
            args.weread_script,
            ["underlines", f"--bookId={args.book_id}", f"--chapterUid={args.chapter_uid}"],
        )
        highlights.extend(extract_highlights(payload))
    if not args.book_title or not args.chapter_title:
        print("after-read 需要 --book-title 和 --chapter-title", file=sys.stderr)
        return 2
    result = build_after_read_result(
        AfterReadInput(
            book_title=args.book_title,
            chapter_title=args.chapter_title,
            current_problem=args.current_problem or "",
            highlights=highlights,
        )
    )
    if args.writeback and result.should_writeback:
        config = _load_config_or_chat(args.config)
        write_result = write_action_card(
            result.markdown,
            config,
            f"{args.book_title}-{args.chapter_title}",
            output_dir=args.writeback_dir,
        )
        print(write_result.message)
        if write_result.path is None:
            print(result.markdown)
        return 0
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result.markdown.rstrip() + "\n", encoding="utf-8")
        print(f"已写入：{args.output}")
        return 0
    print(result.markdown)
    return 0


def _cmd_weekly(args: argparse.Namespace) -> int:
    report = build_weekly_report(WeeklyReportInput(cards=load_cards(args.cards), context=args.context or ""))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
        print(f"已写入周复盘：{args.output}")
    else:
        print(report)
    return 0


def _cmd_today(args: argparse.Namespace) -> int:
    script = Path(__file__).resolve().parents[1] / "scripts" / "today_live.py"
    command = [
        sys.executable,
        str(script),
        "--config",
        str(args.config),
        "--weread-script",
        str(args.weread_script),
        "--limit-books",
        str(args.limit_books),
        "--notebooks-count",
        str(args.notebooks_count),
    ]
    if args.brief:
        command.extend(["--brief", args.brief])
    result = subprocess.run(command, text=True)
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="carl-weread V0.3 unified reading coach CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    recommend = subparsers.add_parser("recommend", help="推荐一本没读透但现在该读的书")
    recommend.add_argument("--config", type=Path, default=default_config_path())
    recommend.add_argument("--weread-script", type=Path, default=Path("scripts/weread.sh"))
    recommend.add_argument("--brief", help="当前问题/项目上下文")
    recommend.add_argument("--keyword", help="额外搜索关键词")
    recommend.add_argument("--similar-book-id", action="append", help="用相似书扩展候选，可传多次")
    recommend.add_argument("--count", type=int, default=12)
    recommend.add_argument("--notebooks-count", type=int, default=200)
    recommend.add_argument("--json", action="store_true")
    recommend.set_defaults(func=_cmd_recommend)

    today = subparsers.add_parser("today", help="推荐今天只读哪一小节")
    today.add_argument("--config", type=Path, default=default_config_path())
    today.add_argument("--weread-script", type=Path, default=Path("scripts/weread.sh"))
    today.add_argument("--brief", help="当前问题/项目上下文")
    today.add_argument("--limit-books", type=int, default=5)
    today.add_argument("--notebooks-count", type=int, default=200)
    today.set_defaults(func=_cmd_today)

    after_read = subparsers.add_parser("after-read", help="读后检查划线；有划线生成行动卡，无划线走追问协议")
    after_read.add_argument("--config", type=Path, default=default_config_path())
    after_read.add_argument("--weread-script", type=Path, default=Path("scripts/weread.sh"))
    after_read.add_argument("--book-id")
    after_read.add_argument("--chapter-uid")
    after_read.add_argument("--book-title")
    after_read.add_argument("--chapter-title")
    after_read.add_argument("--current-problem")
    after_read.add_argument("--highlight", action="append")
    after_read.add_argument("--highlights-file", type=Path)
    after_read.add_argument("--auto-fetch", action="store_true")
    after_read.add_argument("--writeback", action="store_true")
    after_read.add_argument("--writeback-dir", type=Path)
    after_read.add_argument("--output", type=Path)
    after_read.set_defaults(func=_cmd_after_read)

    weekly = subparsers.add_parser("weekly", help="从阅读行动卡生成周复盘")
    weekly.add_argument("--cards", nargs="*", type=Path, default=[])
    weekly.add_argument("--context", default="")
    weekly.add_argument("--output", type=Path)
    weekly.set_defaults(func=_cmd_weekly)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
