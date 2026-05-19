import subprocess
import sys
from pathlib import Path

import pytest

from carl_weread.config import ContextConfig, load_config, write_config


ROOT = Path(__file__).resolve().parents[1]


def test_write_and_load_folder_config_without_storing_api_key(tmp_path, monkeypatch):
    notes = tmp_path / "notes"
    notes.mkdir()
    config_path = tmp_path / "carl-weread.toml"
    monkeypatch.setenv("WEREAD_API_KEY", "wrk-secret-should-not-be-written")

    write_config(ContextConfig(mode="folder", path=notes), config_path)

    raw = config_path.read_text(encoding="utf-8")
    assert "mode = \"folder\"" in raw
    assert str(notes) in raw
    assert "wrk-secret" not in raw

    loaded = load_config(config_path)
    assert loaded.mode == "folder"
    assert loaded.path == notes


def test_file_based_modes_require_path(tmp_path):
    with pytest.raises(ValueError, match="path is required"):
        write_config(ContextConfig(mode="obsidian"), tmp_path / "config.toml")


def test_chat_and_weread_only_modes_do_not_require_path(tmp_path):
    chat_path = tmp_path / "chat.toml"
    write_config(ContextConfig(mode="chat"), chat_path)
    assert load_config(chat_path).path is None

    weread_path = tmp_path / "weread.toml"
    write_config(ContextConfig(mode="weread-only"), weread_path)
    assert load_config(weread_path).path is None


def test_setup_script_writes_config_non_interactively(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    output = tmp_path / "config.toml"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "setup.py"),
            "--mode",
            "folder",
            "--path",
            str(notes),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "已写入配置" in result.stdout
    assert load_config(output).mode == "folder"
