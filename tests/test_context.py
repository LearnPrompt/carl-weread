from datetime import date

from carl_weread.context import collect_recent_context


def test_collect_recent_context_reads_daily_project_and_topic_files(tmp_path):
    vault = tmp_path / "vault"
    (vault / "10_日记").mkdir(parents=True)
    (vault / "20_项目" / "carl-weread").mkdir(parents=True)
    (vault / "15_自媒体" / "选题库").mkdir(parents=True)

    (vault / "10_日记" / "2026-05-18.md").write_text("今天在做 Agent Skill 和微信读书。", encoding="utf-8")
    (vault / "20_项目" / "carl-weread" / "README.md").write_text("项目目标：每天推荐一小节。", encoding="utf-8")
    (vault / "15_自媒体" / "选题库" / "读书工作流.md").write_text("选题：AI 时代读书从问题开始。", encoding="utf-8")

    items = collect_recent_context(vault, today=date(2026, 5, 18), days=1, max_chars_per_file=80)

    assert [item.kind for item in items] == ["daily", "project", "topic"]
    assert any("Agent Skill" in item.text for item in items)
    assert any("每天推荐一小节" in item.text for item in items)
    assert any("AI 时代读书" in item.text for item in items)
