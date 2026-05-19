from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .reading_profile import BookProfile, extract_book_profiles, merge_profiles
from .today_chapter import ContextItem, _expanded_tokens


@dataclass(frozen=True)
class UnreadRecommendation:
    book_id: str
    book_title: str
    author: str
    source: str
    why: str
    evidence: list[str]
    first_reading_question: str
    next_action: str


def _context_text(context: list[ContextItem], brief: str = "") -> str:
    return "\n".join([brief, *(item.text for item in context)]).strip()


def _known_ids(*groups: list[BookProfile]) -> set[str]:
    return {profile.book_id for group in groups for profile in group}


def _tokens_for_profile(profile: BookProfile) -> set[str]:
    return _expanded_tokens(" ".join([profile.title, profile.author, profile.category, profile.intro]))


def _score_profile(profile: BookProfile, context_tokens: set[str], shelf_ids: set[str], notebook_ids: set[str]) -> tuple[int, str]:
    profile_tokens = _tokens_for_profile(profile)
    overlap = context_tokens & profile_tokens
    score = len(overlap) * 10
    reasons: list[str] = []
    if overlap:
        reasons.append("命中当前问题关键词：" + "、".join(sorted(overlap)[:5]))
    if profile.book_id not in shelf_ids:
        score += 8
        reasons.append("不在当前书架里，更像真正的新候选")
    elif profile.book_id not in notebook_ids:
        score += 4
        reasons.append("在书架里但还没有明显笔记痕迹")
    if "recommend" in profile.source:
        score += 3
        reasons.append("来自微信读书个性化推荐")
    if "similar" in profile.source:
        score += 2
        reasons.append("来自相似书扩展")
    if "search" in profile.source:
        score += 1
        reasons.append("来自当前问题搜索")
    return score, "；".join(reasons) or "候选来源完整，但和当前问题的文本重合较少"


def recommend_unread_book(
    context: list[ContextItem],
    shelf_payload: Any,
    notebooks_payload: Any,
    recommendation_payloads: list[Any] | None = None,
    similar_payloads: list[Any] | None = None,
    search_payloads: list[Any] | None = None,
    brief: str = "",
) -> UnreadRecommendation:
    """Recommend one not-yet-digested book using shelf, notes and candidate sources."""
    shelf = extract_book_profiles(shelf_payload, source="shelf")
    notebooks = extract_book_profiles(notebooks_payload, source="notebooks")
    recommended = [
        profile
        for payload in (recommendation_payloads or [])
        for profile in extract_book_profiles(payload, source="recommend")
    ]
    similar = [
        profile
        for payload in (similar_payloads or [])
        for profile in extract_book_profiles(payload, source="similar")
    ]
    search = [
        profile
        for payload in (search_payloads or [])
        for profile in extract_book_profiles(payload, source="search")
    ]
    candidates = merge_profiles(recommended, similar, search, shelf)
    if not candidates:
        raise ValueError("no book candidates")

    shelf_ids = _known_ids(shelf)
    notebook_ids = _known_ids(notebooks)
    context_tokens = _expanded_tokens(_context_text(context, brief))

    ranked = []
    for profile in candidates:
        if profile.book_id in notebook_ids and profile.note_count > 0:
            continue
        score, reason = _score_profile(profile, context_tokens, shelf_ids, notebook_ids)
        ranked.append((score, profile, reason))
    if not ranked:
        raise ValueError("no unread candidates after filtering notebook evidence")

    ranked.sort(key=lambda item: (item[0], item[1].title), reverse=True)
    score, chosen, reason = ranked[0]
    evidence = [reason]
    if chosen.book_id in shelf_ids:
        evidence.append("书架里能看到这本书，但当前笔记列表没有显示已消化证据。")
    else:
        evidence.append("书架和笔记中暂未看到这本书，适合作为新输入。")
    if chosen.category:
        evidence.append(f"分类线索：{chosen.category}")
    if chosen.intro:
        clean_intro = re.sub(r"\s+", " ", chosen.intro).strip()[:120]
        evidence.append(f"简介线索：{clean_intro}")

    return UnreadRecommendation(
        book_id=chosen.book_id,
        book_title=chosen.title,
        author=chosen.author,
        source=chosen.source,
        why=f"这本书和当前问题最接近，同时没有明显读后笔记证据。评分口径是：当前上下文匹配、是否已在书架、是否已有笔记、候选来源可信度。",
        evidence=evidence,
        first_reading_question="翻开后先看目录，只问：哪一章能解释我现在最卡的那个问题？",
        next_action="不要先通读。先选一个章节，读完只写一条划线和一张行动卡。",
    )


def format_unread_recommendation(rec: UnreadRecommendation) -> str:
    author = f"｜{rec.author}" if rec.author else ""
    lines = [
        "今天推荐一本没读透但现在该读的书：",
        f"《{rec.book_title}》{author}",
        "",
        "为什么是它：",
        rec.why,
        "",
        "证据：",
        *[f"- {item}" for item in rec.evidence],
        "",
        "读前问题：",
        rec.first_reading_question,
        "",
        "读完只做一个动作：",
        rec.next_action,
    ]
    return "\n".join(lines)
