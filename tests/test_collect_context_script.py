import subprocess
import sys
from pathlib import Path

from carl_weread.config import ContextConfig, write_config


ROOT = Path(__file__).resolve().parents[1]


def test_collect_context_script_accepts_config_and_brief(tmp_path):
    config_path = tmp_path / "config.toml"
    write_config(ContextConfig(mode="chat"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "collect_context.py"),
            "--config",
            str(config_path),
            "--brief",
            "今天想把微信读书做成一个可分享 skill。",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "## brief: current-input" in result.stdout
    assert "可分享 skill" in result.stdout
