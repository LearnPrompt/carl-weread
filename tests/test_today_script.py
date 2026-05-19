import json
import subprocess
import sys
from pathlib import Path

from carl_weread.config import ContextConfig, write_config


ROOT = Path(__file__).resolve().parents[1]


def test_today_script_connects_config_context_and_candidate_chapters(tmp_path):
    config_path = tmp_path / "config.toml"
    write_config(ContextConfig(mode="chat"), config_path)
    chapters_path = tmp_path / "chapters.json"
    chapters_path.write_text(
        json.dumps(
            [
                {"book_id": "b1", "book_title": "小说写作课", "chapter_uid": "1", "title": "人物弧光"},
                {
                    "book_id": "b2",
                    "book_title": "AI Harness Engineering",
                    "chapter_uid": "7",
                    "title": "Agent Skill 交付验证",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "today.py"),
            "--config",
            str(config_path),
            "--brief",
            "我今天在做 Agent Skill，要把能力做成可验证交付。",
            "--chapters",
            str(chapters_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "今天只读这一小节" in result.stdout
    assert "《AI Harness Engineering》｜Agent Skill 交付验证" in result.stdout
    assert "weread://reading?bId=b2&chapterUid=7" in result.stdout
