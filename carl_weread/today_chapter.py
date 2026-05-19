from __future__ import annotations

from dataclasses import dataclass
import re

from .formatting import weread_link


@dataclass(frozen=True)
class ContextItem:
    kind: str
    source: str
    text: str


@dataclass(frozen=True)
class Chapter:
    book_id: str
    book_title: str
    chapter_uid: str
    title: str


@dataclass(frozen=True)
class TodayChapterRecommendation:
    book_title: str
    chapter_title: str
    why: str
    reading_question: str
    apply_action: str
    deep_link: str


_KEYWORD_ALIASES = {
    "agent": ["agent", "skill", "subagent", "codex", "hermes", "ai software", "harness"],
    "product": ["产品", "pm", "用户", "增长", "需求"],
    "writing": ["写作", "选题", "公众号", "脚本", "内容"],
    "design": ["设计", "审美", "ui", "ux", "视觉"],
}

_NON_CONTENT_CHAPTER_TITLES = {
    "封面",
    "目录",
    "版权",
    "版权页",
    "版权信息",
    "书名页",
    "扉页",
    "献词",
    "插图",
    "插图目录",
    "内容简介",
    "作者简介",
    "前言",
    "序",
    "推荐序",
    "作者序",
    "再版序",
}

_BRIEF_TRIGGER_PHRASES = {
    "今天读什么",
    "今天读哪一小节",
    "推荐一章",
    "推荐一小节",
}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_-]*|[\u4e00-\u9fff]{2,}", text)}


def _expanded_tokens(text: str) -> set[str]:
    tokens = _tokens(text)
    expanded = set(tokens)
    joined = " ".join(tokens)
    for key, aliases in _KEYWORD_ALIASES.items():
        if any(alias.lower() in joined for alias in aliases):
            expanded.update(alias.lower() for alias in aliases)
            expanded.add(key)
    return expanded


def is_substantive_chapter_title(title: str) -> bool:
    normalized = re.sub(r"\s+", "", title).strip("：:,.，。！？!?")
    if not normalized:
        return False
    return normalized not in _NON_CONTENT_CHAPTER_TITLES


def _has_specific_context(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text).strip("：:,.，。！？!?")
    if not normalized:
        return False
    return normalized not in _BRIEF_TRIGGER_PHRASES


def choose_today_chapter(context: list[ContextItem], chapters: list[Chapter]) -> TodayChapterRecommendation:
    """Pick the chapter most connected to the current context."""
    chapters = [chapter for chapter in chapters if is_substantive_chapter_title(chapter.title)]
    if not chapters:
        raise ValueError("chapters must not be empty")
    context_text = "\n".join(item.text for item in context)
    context_tokens = _expanded_tokens(context_text)

    def score(chapter: Chapter) -> int:
        chapter_tokens = _expanded_tokens(f"{chapter.book_title} {chapter.title}")
        return len(context_tokens & chapter_tokens)

    chosen = max(chapters, key=score)
    strongest_context = context[0].text if context else "最近上下文不足"
    short_context = strongest_context.replace("\n", " ")[:80]
    if _has_specific_context(context_text):
        why = f"你最近的上下文里反复出现「{short_context}」，这一节最接近当前问题。"
    else:
        why = "当前没有可用的项目/笔记上下文；我先按微信读书最近书架和笔记里的可读章节推荐这一节。"

    return TodayChapterRecommendation(
        book_title=chosen.book_title,
        chapter_title=chosen.title,
        why=why,
        reading_question="读这一节时只问一个问题：它能解释我最近哪个真实卡点？",
        apply_action="读完后写下一条可以在今天项目里立刻改掉的动作。",
        deep_link=weread_link(chosen.book_id, chosen.chapter_uid),
    )
