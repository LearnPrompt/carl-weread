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
    print(json.dumps({"data": {"books": [{"bookId": "b1", "title": "AI Harness Engineering"}]}}))
elif cmd == "notebooks":
    print(json.dumps({"data": {"books": [{"bookId": "b2", "title": "写作是门手艺"}]}}))
elif cmd == "chapters":
    book_id = next(arg.split("=", 1)[1] for arg in sys.argv[2:] if arg.startswith("--bookId="))
    titles = {"b1": "Agent Skill 交付验证", "b2": "从真实问题开始写"}
    print(json.dumps({"data": {"chapters": [{"chapterUid": "c-" + book_id, "title": titles[book_id]}]}}))
else:
    raise SystemExit(9)
""".strip(),
        encoding="utf-8",
    )


def test_today_live_script_fetches_candidates_and_prints_recommendation(tmp_path):
    fake_weread = tmp_path / "fake_weread.py"
    _write_fake_weread(fake_weread)
    config_path = tmp_path / "config.toml"
    write_config(ContextConfig(mode="chat"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "today_live.py"),
            "--config",
            str(config_path),
            "--weread-script",
            str(fake_weread),
            "--brief",
            "我今天在做 Agent Skill，要把能力做成可验证交付。",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "今天只读这一小节" in result.stdout
    assert "《AI Harness Engineering》｜Agent Skill 交付验证" in result.stdout
    assert "weread://reading?bId=b1&chapterUid=c-b1" in result.stdout
    assert not (tmp_path / "candidates.json").exists()


def test_today_live_script_does_not_accept_api_key_as_argument(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "today_live.py"),
            "--api-key",
            "wrk-secret",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "wrk-secret" not in result.stdout
