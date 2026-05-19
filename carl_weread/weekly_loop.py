from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class WeeklyReportInput:
    cards: list[str]
    context: str = ""


def _first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "未命名阅读卡"


def _section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^## ", markdown[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(markdown)
    return markdown[start:end].strip()


def load_cards(paths: list[str | Path]) -> list[str]:
    cards: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if path.is_dir():
            files = sorted(path.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
            cards.extend(p.read_text(encoding="utf-8", errors="ignore") for p in files)
        elif path.exists():
            cards.append(path.read_text(encoding="utf-8", errors="ignore"))
    return [card for card in cards if card.strip()]


def build_weekly_report(report_input: WeeklyReportInput) -> str:
    """Build a concise weekly reading-action report from action cards and context."""
    cards = report_input.cards
    headings = [_first_heading(card) for card in cards]
    actions = [_section(card, "可以马上改的一个动作") for card in cards]
    topics = [_section(card, "可发展的内容选题") for card in cards]
    problems = [_section(card, "它解释了我最近哪个问题") for card in cards]
    evidence = [action for action in actions if action]

    if not cards:
        main_reading = "本周还没有可复盘的阅读行动卡。"
        evidence_block = "没有证据。先完成一次 today → after-read，再复盘。"
        impact_block = "阅读还没有进入文章、项目或判断。"
        escape_block = "如果只是收藏书和章节，但没有行动卡，就算作逃避式收藏。"
        next_line = "下周只做一件事：完成一张阅读行动卡。"
        stop_line = "先停止扩书单，直到第一张行动卡出现。"
        candidates = ["从当前最卡的问题开始，而不是从书单开始。"]
    else:
        main_reading = "\n".join(f"- {heading}" for heading in headings[:5])
        evidence_block = "\n".join(f"- {item.splitlines()[0]}" for item in evidence[:5]) or "还缺少行动证据。"
        impact_block = _derive_impact(report_input.context, problems, topics)
        escape_block = "没有行动卡支撑的章节先不算读进去；下周减少只收藏不应用的阅读。"
        next_line = _derive_next_line(report_input.context, headings, topics)
        stop_line = _derive_stop_line(headings, evidence)
        candidates = _derive_candidates(headings, topics)

    return "\n".join([
        "# 本周阅读行动闭环",
        "",
        "## 本周真正读进去的东西",
        main_reading,
        "",
        "## 已经进入工作的证据",
        evidence_block,
        "",
        "## 阅读影响",
        impact_block,
        "",
        "## 逃避式收藏",
        escape_block,
        "",
        "## 下周停止读什么",
        stop_line,
        "",
        "## 下周只保留一条阅读主线",
        next_line,
        "",
        "## 下周 3 个 Today Chapter 候选",
        *[f"{idx}. {candidate}" for idx, candidate in enumerate(candidates[:3], start=1)],
    ]).strip()


def _derive_next_line(context: str, headings: list[str], topics: list[str]) -> str:
    text = " ".join([context, *headings, *topics])
    if any(word in text for word in ("文章", "选题", "公众号", "内容", "脚本")):
        return "把阅读服务于一篇可发布内容：每次读完只沉淀一个能进入文章的判断。"
    if any(word.lower() in text.lower() for word in ("agent", "skill", "workflow", "hermes")):
        return "把阅读服务于一个可演示工作流：每次读完只改进一个可验证动作。"
    return "把阅读服务于当前最卡的项目：每次读完只推进一个今天能完成的小动作。"


def _derive_impact(context: str, problems: list[str], topics: list[str]) -> str:
    text = " ".join([context, *problems, *topics])
    if any(word in text for word in ("文章", "选题", "公众号", "脚本", "内容")):
        return "本周阅读已经进入内容生产：优先把行动卡里的判断改写成文章段落或视频脚本测试点。"
    if any(word.lower() in text.lower() for word in ("agent", "skill", "workflow", "cli", "hermes")):
        return "本周阅读已经进入产品/工程判断：优先把行动卡里的概念变成可运行命令、测试或README说明。"
    if any(item.strip() for item in problems):
        return "本周阅读至少解释了一个真实问题；下周要看它有没有改变具体行动。"
    return "行动卡里还缺少清晰问题，影响证据偏弱。下周先补「它解释了我最近哪个问题」。"


def _derive_stop_line(headings: list[str], evidence: list[str]) -> str:
    if not evidence:
        return "停止继续收藏新书；先把本周已读章节补成一张能行动的卡。"
    if len(headings) >= 4:
        return "停止横向开新主题；下周只沿着最有行动证据的一条线往下读。"
    return "停止为了安心而补书单；只保留能推动当前动作的章节。"


def _derive_candidates(headings: list[str], topics: list[str]) -> list[str]:
    candidates: list[str] = []
    for heading in headings[:3]:
        candidates.append(f"延续 {heading}：找下一节能直接改动作的内容")
    for topic in topics:
        lines = topic.splitlines()
        if not lines:
            continue
        first = lines[0].replace("标题方向：", "").strip()
        if first:
            candidates.append(f"围绕「{first}」补一节案例型阅读")
    candidates.append("从本周最卡的项目问题倒推一节书，而不是顺着目录读。")
    return candidates[:3]
