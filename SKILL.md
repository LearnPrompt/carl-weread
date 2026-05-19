---
name: carl-weread
description: 微信读书行动型阅读教练。根据用户最近的 Obsidian 日记、项目、选题和微信读书书架/笔记，推荐今天最该读的一小节，并把读后收获转成行动卡、原子笔记和内容选题线索。当用户说「今天读什么」「推荐一章」「读完了帮我消化」「把阅读变成行动」「本周阅读闭环」时触发。
version: 0.2.0
author: Carl / LearnPrompt
license: MIT
metadata:
  hermes:
    tags: [weread, reading, obsidian, agent-skill, knowledge-workflow]
    related_skills: [obsidian, chinese-content-workflows]
---

# carl-weread

## 定位

`carl-weread` 不是阅读统计，不是通用书单，也不是年度报告。

它是「上下文驱动的阅读行动系统」：根据用户最近真实在做的事，从微信读书里找一个今天能读完的小阅读块，并把读后收获接回项目、笔记和内容生产。

## 何时使用

用户出现以下意图时使用：

- 今天读什么 / 推荐一章 / 推荐一小节
- 根据我最近在做的事找一本书里的章节
- 读完了，帮我消化
- 把这次阅读变成行动卡 / Obsidian 笔记 / 选题线索
- 本周阅读闭环 / 哪些阅读真的进入工作了

不要用于：

- 只想生成完整阅读可视化报告：建议转向 `yao-weread-skill` 类工作流。
- 只想把 Markdown 做成 EPUB：建议转向 `qiaomu-epub-book-generator` 类工作流。
- 只想系统规划一个新领域书单：可借鉴 `huashu-weread` 的 path 思路。

## 工作流路由

| 用户意图 | 工作流 |
|---|---|
| 今天读什么 / 推荐一章 | `workflows/today-chapter.md` |
| 读完了 / 帮我消化 | `workflows/digest-apply.md` |
| 本周阅读复盘 | `workflows/weekly-loop.md` |

## 强制规则

1. 不允许只推荐书名；必须尽量定位到章节或小节。
2. 推荐理由必须连接用户最近真实上下文，不能只说「这本书很好」。
3. 输出必须包含一个读前问题和一个读后行动。
4. 能生成 `weread://` 链接时必须生成。
5. 如果上下文不足，先退化为「基于微信读书最近阅读推荐」，并明确说明口径。
6. 不导出书籍全文；只使用微信读书 API 可访问的元数据、用户自己的笔记/划线、公开热度信息。
7. 不打印 `WEREAD_API_KEY`；如需持久化，只能写入 `~/.config/carl-weread/api_key` 这种权限为 `600` 的私有 key 文件，不能写入 `config.toml`、README、日志或普通 shell 配置。

## 数据源

| 数据 | 来源 | 用途 |
|---|---|---|
| 最近日记 | Obsidian `10_日记/` | 判断当下关注点 |
| 活跃项目 | Obsidian `20_项目/` | 判断真实任务压力 |
| 选题库 | Obsidian `15_自媒体/选题库/` | 判断内容生产方向 |
| 普通本地笔记 | 任意 Markdown/TXT 文件夹 | 无 Obsidian 用户的上下文降级 |
| 当前对话/用户 brief | 用户本轮输入 | 无本地笔记时的轻量上下文 |
| 书架 | WeRead `/shelf/sync` | 找已有书和最近活跃书 |
| 笔记概览 | WeRead `/user/notebooks` | 判断真读过什么 |
| 章节目录 | WeRead `/book/chapterinfo` | 定位章节 |
| 阅读进度 | WeRead `/book/getprogress` | 避免推荐不合适章节 |

## 安装/依赖原则

- 不强制先安装官方 WeRead Skill；本 skill 自带 `scripts/weread.sh` 作为 API helper。
- 必须配置 `WEREAD_API_KEY` 或私有 key 文件，Key 从官方微信读书 Skill/API 入口获取。
- Obsidian 不是硬依赖；有 Obsidian 时走 Full Mode，没有 Obsidian 时按「普通文件夹 → 当前对话 brief → WeRead-only」逐级降级。

## 调用约定

- 首次上下文配置通过 `scripts/setup.py --mode ...` 写入 `~/.config/carl-weread/config.toml`。
- 首次 API Key 配置优先通过 `scripts/setup_api_key.py` 写入 `~/.config/carl-weread/api_key`；也支持临时环境变量 `WEREAD_API_KEY`。
- 微信读书 API 通过 `scripts/weread.sh` 调用。
- 上下文通过 `scripts/collect_context.py --config ...`、`carl_weread.context.collect_context_for_config` 或 `carl_weread.context.collect_recent_context` 收集。
- 今日推荐优先用 `scripts/today_live.py --brief ...` 一键执行真实 WeRead 拉取和推荐。
- 候选章节可以用 `scripts/fetch_candidates.py --output ...` 从真实 WeRead API 拉取，或用 `scripts/build_candidates.py` 从已保存 JSON 离线生成。
- 调试时也可以用 `scripts/today.py --config ... --chapters ...` 串联本地候选章节验证。
- 读后消化用 `scripts/digest_apply.py`，可打印行动卡、写到指定 `--output`，或 `--writeback` 写回配置目标。
- 周复盘用 `scripts/weekly_loop.py --cards ... --context ...`。
- 章节选择逻辑通过 `carl_weread.today_chapter` 执行。
- 输出格式遵守 `shared/output-style.md`。

## Common Pitfalls

1. **推一本书而不是一小节。** 修正：优先查章节目录，给今天能读完的阅读块。
2. **只看书架不看笔记。** 修正：书架表示兴趣，笔记表示真读过，必须交叉。
3. **读完只总结不行动。** 修正：每次 digest 必须生成一个可执行动作。
4. **用泛泛的 AI 话术解释推荐。** 修正：必须引用用户最近上下文中的真实任务或问题。
5. **输出裸 bookId。** 修正：尽量隐藏在 `weread://` 深度链接里。

## Verification Checklist

- [ ] `scripts/weread.sh --help` 可运行。
- [ ] `scripts/today_live.py --brief ...` 可生成今日一小节。
- [ ] `scripts/digest_apply.py ... --writeback` 可生成/写回阅读行动卡。
- [ ] `scripts/weekly_loop.py --cards ...` 可生成周复盘。
- [ ] `python -m pytest tests -q` 通过。
- [ ] `SKILL.md` frontmatter 合法，description 未超 1024 字符。
- [ ] 三个 workflow 文件存在。
- [ ] README 能让第一次看到的人理解差异化和完整安装方式。
