from datetime import date

from carl_weread.config import ContextConfig
from carl_weread.context import collect_context_for_config


def test_collect_context_for_folder_config_reads_plain_notes(tmp_path):
    notes = tmp_path / "notes"
    notes.mkdir()
    (notes / "work.md").write_text("今天的问题是把微信读书变成行动。", encoding="utf-8")

    items = collect_context_for_config(
        ContextConfig(mode="folder", path=notes),
        today=date(2026, 5, 18),
        max_chars_per_file=80,
    )

    assert len(items) == 1
    assert items[0].kind == "context"
    assert "行动" in items[0].text


def test_collect_context_for_chat_config_uses_brief():
    items = collect_context_for_config(ContextConfig(mode="chat"), brief="我最近卡在读书和项目连接不上。")

    assert len(items) == 1
    assert items[0].kind == "brief"
    assert items[0].source == "current-input"
    assert "项目连接不上" in items[0].text


def test_collect_context_for_weread_only_config_returns_empty_context():
    assert collect_context_for_config(ContextConfig(mode="weread-only"), brief="忽略这句") == []
