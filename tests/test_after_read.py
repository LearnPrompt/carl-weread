from carl_weread.after_read import AfterReadInput, build_after_read_result, extract_highlights


def test_after_read_with_highlights_builds_action_card():
    result = build_after_read_result(
        AfterReadInput(
            book_title="AI Harness Engineering",
            chapter_title="验证章节",
            current_problem="把 Skill 做成可验证交付",
            highlights=["Agent 工作流需要可观测的验证标准。"],
        )
    )

    assert result.status == "action-card"
    assert result.should_writeback is True
    assert "# 阅读行动卡｜《AI Harness Engineering》验证章节" in result.markdown
    assert "Agent 工作流需要可观测的验证标准" in result.markdown


def test_after_read_without_highlights_uses_socratic_protocol():
    result = build_after_read_result(
        AfterReadInput(
            book_title="写作是门手艺",
            chapter_title="从真实问题开始写",
            current_problem="选题太散",
            highlights=[],
        )
    )

    assert result.status == "no-highlights"
    assert result.should_writeback is False
    assert "无划线读后检查" in result.markdown
    assert "先回答 3 个问题" in result.markdown
    assert "选题太散" in result.markdown


def test_extract_highlights_handles_underlines_payload():
    payload = {
        "data": {
            "updated": [
                {"markText": "第一条划线"},
                {"abstract": "第二条划线"},
                {"content": ""},
            ]
        }
    }

    assert extract_highlights(payload) == ["第一条划线", "第二条划线"]
