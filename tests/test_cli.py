import json
import subprocess
import sys
from pathlib import Path

from carl_weread.config import ContextConfig, write_config

ROOT = Path(__file__).resolve().parents[1]


def _write_fake_weread(path: Path) -> None:
    path.write_text(
        """
import json
import sys

cmd = sys.argv[1]
if cmd == "shelf":
    print(json.dumps({"data": {"books": [{"bookId": "s1", "title": "旧书"}]}}))
elif cmd == "notebooks":
    print(json.dumps({"data": {"books": [{"bookId": "n1", "title": "已读书", "noteCount": 3}]}}))
elif cmd == "recommend":
    print(json.dumps({"data": {"books": [{"bookId": "r1", "title": "Agent Workflow Handbook", "author": "A", "intro": "agent workflow skill"}]}}))
elif cmd == "underlines":
    print(json.dumps({"data": {"updated": [{"markText": "这章真正有用的是验证标准。"}]}}))
else:
    raise SystemExit(9)
""".strip(),
        encoding="utf-8",
    )


def test_unified_cli_recommend_uses_weread_sources(tmp_path):
    fake_weread = tmp_path / "fake_weread.py"
    _write_fake_weread(fake_weread)
    config_path = tmp_path / "config.toml"
    write_config(ContextConfig(mode="chat"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "carl_weread.py"),
            "recommend",
            "--config",
            str(config_path),
            "--weread-script",
            str(fake_weread),
            "--brief",
            "我在做 Agent workflow",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "今天推荐一本没读透但现在该读的书" in result.stdout
    assert "Agent Workflow Handbook" in result.stdout


def test_unified_cli_after_read_auto_fetch_builds_card(tmp_path):
    fake_weread = tmp_path / "fake_weread.py"
    _write_fake_weread(fake_weread)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "carl_weread.py"),
            "after-read",
            "--weread-script",
            str(fake_weread),
            "--book-id",
            "b1",
            "--chapter-uid",
            "c1",
            "--book-title",
            "AI Harness Engineering",
            "--chapter-title",
            "验证章节",
            "--current-problem",
            "做出V0.3",
            "--auto-fetch",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "# 阅读行动卡" in result.stdout
    assert "验证标准" in result.stdout


def test_unified_cli_weekly_prints_report(tmp_path):
    card = tmp_path / "card.md"
    card.write_text(
        "# 阅读行动卡｜《AI Harness》验证章节\n\n## 可以马上改的一个动作\n把 CLI 做成一个入口。\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "carl_weread.py"),
            "weekly",
            "--cards",
            str(tmp_path),
            "--context",
            "我在做 Agent Skill 文章",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "# 本周阅读行动闭环" in result.stdout
    assert "把 CLI 做成一个入口" in result.stdout
