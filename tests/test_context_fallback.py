from datetime import date

from carl_weread.context import collect_recent_context


def test_collect_recent_context_supports_generic_folder_without_obsidian_structure(tmp_path):
    notes = tmp_path / "my-notes"
    notes.mkdir()
    (notes / "current-work.md").write_text("我最近在做微信读书 skill，要推荐今天读哪一小节。", encoding="utf-8")
    (notes / "idea.txt").write_text("读书应该从当前问题开始，而不是从书单开始。", encoding="utf-8")

    items = collect_recent_context(notes, today=date(2026, 5, 18), days=3, max_chars_per_file=80)

    assert [item.kind for item in items] == ["context", "context"]
    assert any("微信读书 skill" in item.text for item in items)
    assert any("当前问题" in item.text for item in items)
