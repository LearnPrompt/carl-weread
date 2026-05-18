from carl_weread.today_chapter import Chapter, ContextItem, choose_today_chapter


def test_choose_today_chapter_prefers_chapter_matching_current_context():
    context = [
        ContextItem(kind="daily", source="2026-05-18.md", text="最近在做 Agent Skill、subagent 和交付质量验证。"),
        ContextItem(kind="project", source="PROJECT.md", text="目标是把阅读接回真实项目行动。"),
    ]
    chapters = [
        Chapter(book_id="b1", book_title="小说写作课", chapter_uid="1", title="人物弧光"),
        Chapter(book_id="b2", book_title="AI Harness Engineering", chapter_uid="7", title="The four-layer view of AI software"),
        Chapter(book_id="b3", book_title="设计心理学", chapter_uid="3", title="门把手与用户心智"),
    ]

    rec = choose_today_chapter(context, chapters)

    assert rec.book_title == "AI Harness Engineering"
    assert rec.chapter_title == "The four-layer view of AI software"
    assert "Agent Skill" in rec.why
    assert rec.reading_question
    assert rec.apply_action
    assert rec.deep_link == "weread://reading?bId=b2&chapterUid=7"
