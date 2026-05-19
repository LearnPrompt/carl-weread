from carl_weread.context import ContextItem
from carl_weread.unread_advisor import format_unread_recommendation, recommend_unread_book


def test_recommend_unread_book_prefers_context_match_without_notebook_evidence():
    shelf = {"data": {"books": [{"bookId": "s1", "title": "旧书：产品增长"}]}}
    notebooks = {"data": {"books": [{"bookId": "n1", "title": "AI Harness Engineering", "noteCount": 12}]}}
    recommend = {
        "data": {
            "books": [
                {"bookId": "n1", "title": "AI Harness Engineering", "author": "A", "intro": "Agent workflow"},
                {"bookId": "r1", "title": "Agent Workflow Handbook", "author": "B", "category": "AI", "intro": "Build reliable agent workflow systems"},
                {"bookId": "r2", "title": "厨房整理术", "author": "C"},
            ]
        }
    }
    context = [ContextItem(kind="brief", source="current", text="我在做 Agent workflow 和 Skill 交付验证。")]

    rec = recommend_unread_book(context, shelf, notebooks, recommendation_payloads=[recommend])

    assert rec.book_id == "r1"
    assert rec.book_title == "Agent Workflow Handbook"
    assert "没有明显读后笔记证据" in rec.why
    assert any("新候选" in item for item in rec.evidence)


def test_format_unread_recommendation_is_action_oriented():
    rec = recommend_unread_book(
        context=[ContextItem(kind="brief", source="current", text="内容选题和写作")],
        shelf_payload={"data": {"books": []}},
        notebooks_payload={"data": {"books": []}},
        recommendation_payloads=[{"data": {"books": [{"bookId": "b1", "title": "写作是门手艺", "author": "作者"}]}}],
    )

    markdown = format_unread_recommendation(rec)

    assert markdown.startswith("今天推荐一本没读透但现在该读的书")
    assert "读前问题" in markdown
    assert "读完只做一个动作" in markdown
