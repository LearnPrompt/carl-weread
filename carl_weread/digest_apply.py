from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReadingInput:
    book_title: str
    chapter_title: str
    highlights: list[str] = field(default_factory=list)
    current_problem: str = ""


def _first_highlight(reading: ReadingInput) -> str:
    return reading.highlights[0].strip() if reading.highlights else "这次阅读需要补一条具体划线或读后想法。"


def _concept_name(reading: ReadingInput) -> str:
    if "验证" in _first_highlight(reading) or "验证" in reading.current_problem:
        return "阅读进入验证链路"
    if "行动" in reading.current_problem:
        return "行动型阅读"
    return "上下文驱动阅读"


def build_action_card(reading: ReadingInput) -> str:
    """Build an Obsidian-ready action card from a reading note."""
    highlight = _first_highlight(reading)
    concept = _concept_name(reading)
    problem = reading.current_problem or "这次阅读还没有绑定到具体问题，需要补充它解释了哪个真实卡点。"

    return f"""# 阅读行动卡｜《{reading.book_title}》{reading.chapter_title}

## 一句话收获
{highlight}

## 它解释了我最近哪个问题
{problem}

## 可以马上改的一个动作
把这次阅读里的一个判断，改写成当前项目里可检查的验证标准，并在今天推进一次。

## 可沉淀的原子笔记
[[{concept}]]：阅读不是在脑子里多存一条知识，而是要进入一个可验证的行动链路。只有能改变下一步动作的内容，才真正进入了工作系统。

## 可发展的内容选题
标题方向：AI 时代读书，不该从书单开始，而该从你今天卡住的问题开始。
切入角度：用《{reading.book_title}》这一节作为例子，展示如何把一段阅读变成一个项目动作。
""".strip()
