from carl_weread.digest_apply import ReadingInput, build_action_card


def test_build_action_card_turns_reading_into_obsidian_ready_markdown():
    reading = ReadingInput(
        book_title="AI Harness Engineering",
        chapter_title="The four-layer view of AI software",
        highlights=["AI 软件要同时看模型、工具、上下文和验证链路。"],
        current_problem="最近在做 carl-weread，需要把 Skill 从 API 调用变成行动闭环。",
    )

    card = build_action_card(reading)

    assert card.startswith("# 阅读行动卡｜《AI Harness Engineering》The four-layer view of AI software")
    assert "## 一句话收获" in card
    assert "验证链路" in card
    assert "## 可以马上改的一个动作" in card
    assert "carl-weread" in card
    assert "[[" in card and "]]" in card
    assert "## 可发展的内容选题" in card
