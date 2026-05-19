import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_fetch_candidates_script_calls_weread_helper_and_writes_candidates(tmp_path):
    fake_weread = tmp_path / "fake_weread.py"
    fake_weread.write_text(
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
    output = tmp_path / "candidates.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fetch_candidates.py"),
            "--weread-script",
            str(fake_weread),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "已获取并写入候选章节" in result.stdout
    data = json.loads(output.read_text(encoding="utf-8"))
    assert [item["book_id"] for item in data] == ["b1", "b2"]
    assert data[0]["title"] == "Agent Skill 交付验证"


def test_fetch_candidates_script_does_not_accept_api_key_as_argument(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "fetch_candidates.py"),
            "--api-key",
            "wrk-secret",
            "--output",
            str(tmp_path / "out.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "wrk-secret" not in result.stdout
