from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .digest_apply import ReadingInput, build_action_card


@dataclass(frozen=True)
class AfterReadInput:
    book_title: str
    chapter_title: str
    current_problem: str = ""
    highlights: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AfterReadResult:
    status: str
    markdown: str
    should_writeback: bool


def extract_highlights(payload: Any) -> list[str]:
    """Extract user highlights from common WeRead bookmark/underline response shapes."""
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = []
        containers = [payload]
        for key in ("data", "result"):
            value = payload.get(key)
            if isinstance(value, dict):
                containers.append(value)
        for container in containers:
            for key in ("updated", "bookmarks", "underlines", "items", "reviews"):
                value = container.get(key)
                if isinstance(value, list):
                    items = value
                    break
            if items:
                break
    else:
        return []

    highlights: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in ("markText", "abstract", "content", "text", "review", "summary"):
            value = item.get(key)
            if value is not None and str(value).strip():
                highlights.append(str(value).strip())
                break
    return highlights


def build_no_highlight_protocol(reading: AfterReadInput) -> str:
    problem = reading.current_problem or "你读这一节前想解决的那个问题"
    return "\n".join(
        [
            f"# 无划线读后检查｜《{reading.book_title}》{reading.chapter_title}",
            "",
            "这次先不强行总结。没有划线时，更可能是读得太散，或者问题没有咬住文本。",
            "",
            "## 先回答 3 个问题",
            f"1. 这一节里哪句话最接近「{problem}」？请补一条原文或自己的转述。",
            "2. 如果只能把这一节变成一个动作，你会改哪个项目、文章或判断？",
            "3. 这节有没有让你改变原来的看法？如果没有，下一次应该换书还是换问题？",
            "",
            "## 下一步",
            "补一条划线/转述后，再生成阅读行动卡；否则这次阅读只记录为浏览，不算进入工作。",
        ]
    )


def build_after_read_result(reading: AfterReadInput) -> AfterReadResult:
    highlights = [item.strip() for item in reading.highlights if item.strip()]
    if not highlights:
        return AfterReadResult(
            status="no-highlights",
            markdown=build_no_highlight_protocol(reading),
            should_writeback=False,
        )
    card = build_action_card(
        ReadingInput(
            book_title=reading.book_title,
            chapter_title=reading.chapter_title,
            highlights=highlights,
            current_problem=reading.current_problem,
        )
    )
    return AfterReadResult(status="action-card", markdown=card, should_writeback=True)
