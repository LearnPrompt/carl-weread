import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_weread_script_without_api_key_fails_safely():
    env = os.environ.copy()
    env.pop("WEREAD_API_KEY", None)
    result = subprocess.run(
        [str(ROOT / "scripts" / "weread.sh"), "shelf"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 3
    assert "缺少 WEREAD_API_KEY" in result.stderr
    assert "wrk-" not in result.stdout
