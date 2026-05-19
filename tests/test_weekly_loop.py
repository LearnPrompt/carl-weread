from carl_weread.weekly_loop import WeeklyReportInput, build_weekly_report, load_cards

CARD = """# 阅读行动卡｜《AI Harness》验证章节

## 可以马上改的一个动作
把 demo 安装链路改成可复制命令。

## 可发展的内容选题
标题方向：为什么 Agent Skill 不能只写提示词
切入角度：用 carl-weread 的安装链路举例。
"""


def test_build_weekly_report_from_cards():
    report = build_weekly_report(WeeklyReportInput(cards=[CARD], context="我在写 Agent Skill 文章"))

    assert report.startswith("# 本周阅读行动闭环")
    assert "阅读行动卡｜《AI Harness》验证章节" in report
    assert "把 demo 安装链路改成可复制命令" in report
    assert "下周只保留一条阅读主线" in report


def test_load_cards_accepts_directory(tmp_path):
    path = tmp_path / "card.md"
    path.write_text(CARD, encoding="utf-8")
    assert load_cards([tmp_path]) == [CARD]
