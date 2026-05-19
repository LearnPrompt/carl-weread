from datetime import date

from carl_weread.config import ContextConfig
from carl_weread.writeback import slugify_title, write_action_card


def test_slugify_title_keeps_readable_chinese_and_removes_bad_chars():
    assert slugify_title("阅读行动卡/第1章: AI?") == "阅读行动卡-第1章-AI"


def test_write_action_card_writes_to_folder_mode(tmp_path):
    config = ContextConfig(mode="folder", path=tmp_path)
    result = write_action_card("card body", config, "AI 工作流", today=date(2026, 5, 19))

    assert result.path == tmp_path / "carl-weread" / "reading-cards" / "2026-05-19-AI-工作流.md"
    assert result.path.read_text(encoding="utf-8") == "card body\n"


def test_write_action_card_chat_mode_does_not_write():
    result = write_action_card("card body", ContextConfig(mode="chat"), "AI 工作流")
    assert result.path is None
    assert "不写文件" in result.message
