<div align="center">

# carl-weread

> 把微信读书从「读了多少」改成「今天哪个问题可以被读懂一点」。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-blueviolet)](SKILL.md)
[![WeRead API](https://img.shields.io/badge/WeRead-API-green)](https://weread.qq.com/r/weread-skills)

<br>

**微信读书行动型阅读教练 · 在官方WeRead API之上加一层「问题→章节→行动」工作流**

<br>

官方微信读书Skill已经把书架、搜索、笔记、统计、推荐这些原子能力开放给Agent。能力很强，但它更像「自然语言版API」。你问推荐书，它容易给一批通识书单；你问阅读统计，它告诉你读了多久；你读完一章，它不会主动追问这次阅读有没有进入你的项目、文章和判断。

`carl-weread`想解决另一个问题：**你最近真实卡住的事，微信读书里哪一章、哪一小节，能帮你今天少焦虑一点、少囤一点资料、多做一个判断？**

```text
当前问题 → 书架/笔记/章节交叉 → 今天只读一小节 → 读后行动卡 → Obsidian/本地Markdown回流 → 周阅读行动复盘
```

[看差异](#看差异) · [功能总览](#功能总览) · [核心方法](#核心方法) · [触发话术](#触发话术) · [装上就能用](#装上就能用)

</div>

---

## 看差异

同样一个问题：

> 我最近信息焦虑，总是在囤资料但不产出，今天该读什么？

**裸WeRead/普通推荐容易给：一批信息管理、效率、认知类书单。**

这些书可能都不错，但它没有回答三个关键问题：

- 你到底是缺信息、缺框架，还是缺一个能落地的判断？
- 这本书你是不是已经读过、收藏过、做过笔记？
- 读完以后，怎么证明这次阅读进入了你的文章、项目或选题？

**carl-weread要给的是：一个今天能读完、能行动的小切口。**

```markdown
今天只读这一小节：
《某本书》｜某一章

为什么是它：
你最近的问题不是资料不够，而是问题没有收束。这一节刚好能把「继续搜索」改成「提出一个更好的问题」。

读前问题：
我现在反复搜索，是为了做哪个判断？

读完只做一个动作：
把当前文章选题改写成一个问题句，而不是资料清单。

打开：weread://reading?bId=...&chapterUid=...
```

差距在这里：**普通WeRead回答「有什么书」，carl-weread逼近「你今天到底要用阅读解决哪个问题」。**

---

## 和原版/参考项目的区别

| 项目 | 更像什么 | 强项 | carl-weread的差异 |
|---|---|---|---|
| 官方WeRead Skill | 原子API | 搜索、书架、笔记、统计、推荐接口完整 | 不停在查数据，往「当前问题→章节→行动」走 |
| huashu-weread | 读书顾问 | 书架+笔记交叉，推荐下一本书，规划主题路径 | 借鉴它的交叉验证，但更聚焦「今天只读哪一小节」和读后行动 |
| jerlin-weread | CLI工程底座 | API文档、脚本、字段约束更稳 | 学它的CLI化，但把命令组织成阅读工作流 |
| yao-weread-skill | 阅读报告 | 年度/周期阅读可视化，适合展示 | carl-weread不追求报告漂亮，追求阅读有没有进入工作 |
| 微信读书App自带统计 | 阅读行为记录 | 时长、天数、连续阅读、读完几本 | carl-weread看「哪些阅读改变了项目、文章、判断」 |

一句话定位：

```text
huashu-weread更像「下一本读什么」；
carl-weread更像「今天这个问题，只读哪一节，然后怎么用」。
```

---

## 功能总览

| 能力 | 当前状态 | 做什么 | 典型命令/入口 |
|---|---:|---|---|
| WeRead原子API helper | ✅ 已完成 | 书架、搜索、统计、详情、目录、进度、笔记、划线、点评、推荐 | `scripts/weread.sh ...` |
| 上下文模式 | ✅ 已完成 | 支持Obsidian、普通文件夹、Chat、WeRead-only四档上下文 | `scripts/setup.py --mode ...` |
| 今日一小节 | ✅ 已完成 | 拉取真实WeRead数据，结合上下文推荐一个章节/小节 | `scripts/today_live.py --brief ...` |
| 候选章节构建 | ✅ 已完成 | 从书架、笔记、章节目录构建可调试候选池 | `scripts/fetch_candidates.py` |
| 读后行动卡 | ✅ 已完成 | 把划线/想法和当前问题压成一张行动卡 | `scripts/digest_apply.py ...` |
| 写回Obsidian/本地文件夹 | ✅ 已完成 | 把阅读行动卡写回`carl-weread/reading-cards/` | `--writeback` |
| 周阅读行动复盘 | ✅ 已完成 | 从行动卡生成「哪些阅读真的进入工作」的周复盘 | `scripts/weekly_loop.py --cards ...` |
| API Key安全初始化 | ✅ 已完成 | 将key写入私有文件，权限600，不进仓库 | `scripts/setup_api_key.py` |
| 未读书交叉验证推荐 | 🚧 下一版重点 | 像huashu一样过滤已深读/已收藏，推荐真正没读过但该读的书 | V0.3计划 |
| 苏格拉底式无划线协议 | 🚧 下一版重点 | 读完后先查有没有划线；没有划线就用问题追回理解 | V0.3计划 |
| 统一产品级CLI | 🚧 下一版重点 | 从一堆`scripts/`升级成`carl-weread recommend/after-read/weekly` | V0.3计划 |

---

## 核心方法

`carl-weread`参考了huashu-weread的「书架+笔记交叉分析」，但加了两层自己的约束。

### 1. 先问问题，再找书

很多阅读推荐默认从「主题」开始，比如AI、产品、心理学。`carl-weread`先从用户当前问题开始：

| 用户输入 | 先判断什么 | 阅读目标 |
|---|---|---|
| 我信息焦虑 | 是缺信息，还是缺收束问题的方法 | 减少输入，形成判断 |
| 我写文章卡住了 | 是缺案例，缺结构，还是缺一个反常识角度 | 推进一篇具体内容 |
| 我项目推进慢 | 是缺技术方案，缺产品判断，还是缺下一步动作 | 读完能改一个动作 |
| 我不知道读什么 | 是真没方向，还是收藏太多没有消化 | 少推荐，多收束 |

### 2. 书架、笔记、章节要交叉看

| 数据源 | 接口 | 揭示什么 | 用在什么地方 |
|---|---|---|---|
| 书架 | `/shelf/sync` | 用户主动收藏/分类的兴趣 | 找候选书，不当作真兴趣的唯一证据 |
| 笔记本概览 | `/user/notebooks` | 真读过什么、哪些书有痕迹 | 判断深读、浅读、只收藏 |
| 章节目录 | `/book/chapterinfo` | 今天能不能定位到小节 | 避免只推荐一本书 |
| 阅读进度 | `/book/getprogress` | 是否正在读、读到哪里 | 避免推荐明显不合适的位置 |
| 个人划线 | `/book/bookmarklist` | 用户真正停下来的地方 | 读后行动卡的证据 |
| 热门划线/点评 | `/book/bestbookmarks`、`/review/list` | 大家反复标记的问题 | 辅助判断章节价值 |
| 推荐/相似书 | `/book/recommend`、`/book/similar` | 新候选来源 | V0.3做未读书推荐交叉验证 |

### 3. 阅读统计不比时长，比影响

微信读书已经能告诉你读了多久。`carl-weread`不重复造一个低配统计页。

它关心的是：

```text
这周哪次阅读变成了文章角度？
哪条划线进入了项目决策？
哪本书只是制造了收藏安全感？
下周只保留哪一条阅读主线？
```

所以weekly-loop的输入不是单纯阅读时长，而是：

```text
微信读书统计 + 本周划线/行动卡 + Obsidian项目/选题上下文
```

---

## 触发话术

| 你可以这样说 | 走哪个能力 | 预期输出 |
|---|---|---|
| 今天读哪一小节 | today-chapter | 一本书里的一个章节/小节，附读前问题和行动 |
| 我信息焦虑，帮我少读一点但读准一点 | today-chapter / V0.3 socratic-read | 先收束问题，再推荐小阅读块 |
| 根据我最近在做的事推荐一章 | today-chapter | 结合Obsidian/Folder/Chat上下文推荐章节 |
| 这本书我读到哪了 | 原子能力：progress | 阅读进度和打开链接 |
| 查一下这本书的目录和我的划线 | 原子能力：book-info/bookmarks/chapters | 书籍详情、章节目录、个人划线 |
| 读完了，帮我消化成行动 | digest-apply | 阅读行动卡、一个最小行动、选题线索 |
| 把这次阅读闭环存到Obsidian | writeback | 写入`carl-weread/reading-cards/` |
| 本周阅读行动复盘 | weekly-loop | 本周真正进入工作的阅读、逃避式收藏、下周主线 |
| 给我推荐一本我没读过但现在该读的书 | V0.3 unread-advisor | 交叉验证已读/未读后推荐一本新书 |

---

## 装上就能用

如果只是执行：

```bash
hermes skills install https://raw.githubusercontent.com/LearnPrompt/carl-weread/main/SKILL.md
```

Hermes只会安装`SKILL.md`，适合加载说明，但不会带上`scripts/`、`carl_weread/`和测试文件。

要完整体验这个skill，推荐直接clone整个仓库：

```bash
git clone https://github.com/LearnPrompt/carl-weread ~/.hermes/skills/carl-weread
cd ~/.hermes/skills/carl-weread
python3 -m venv .venv
.venv/bin/python -m pip install -U pip pytest
.venv/bin/python -m pytest tests -q
```

或者在已clone的仓库里执行完整安装脚本：

```bash
scripts/install_skill.py
```

配置微信读书API Key：

```bash
scripts/setup_api_key.py
```

它会把key写入`~/.config/carl-weread/api_key`，文件权限为`600`，不会写入`config.toml`，也不会打印key。

也可以只在当前shell临时使用：

```bash
export WEREAD_API_KEY="wrk-你的微信读书 API Key"
```

API Key获取入口：<https://weread.qq.com/r/weread-skills>

---

## 没有Obsidian怎么用

可以用。Obsidian只是最高配上下文源，不是硬依赖。

| 模式 | 适合谁 | 上下文来源 | 输出能力 |
|---|---|---|---|
| Full Mode | Obsidian用户 | 日记、项目、选题库 + 微信读书 | 最完整的行动闭环 |
| Folder Mode | 有本地笔记但不用Obsidian | 任意Markdown/TXT文件夹 + 微信读书 | 可推荐章节并生成行动卡 |
| Chat Mode | 只在Agent里聊天 | 用户当前一句话/最近对话 + 微信读书 | 轻量推荐今天一小节 |
| WeRead-only Mode | 没有外部笔记 | 书架、笔记、阅读进度 | 基于最近阅读做推荐 |

首次配置示例：

```bash
# Obsidian 用户
scripts/setup.py --mode obsidian --path "/path/to/your/vault"

# 非 Obsidian，但有本地 Markdown/TXT 笔记
scripts/setup.py --mode folder --path "/path/to/your/notes"

# 只使用当前对话上下文
scripts/setup.py --mode chat

# 只使用微信读书数据
scripts/setup.py --mode weread-only
```

配置默认写入：`~/.config/carl-weread/config.toml`。

---

## 一键今日推荐

完成上下文配置和API Key初始化后，日常使用可以直接跑：

```bash
scripts/today_live.py \
  --brief "我今天卡在内容选题和项目推进之间"
```

它会自动完成：

```text
读取配置 → 收集上下文 → 拉微信读书书架/笔记/章节 → 选择今天一小节 → 输出读前问题和读后动作
```

如果只想调试候选章节生成，可以拆开跑：

```bash
scripts/fetch_candidates.py \
  --output .cache/weread/candidates.json \
  --limit-books 5

scripts/today.py \
  --config ~/.config/carl-weread/config.toml \
  --brief "我最近在做一个可分享的微信读书 skill" \
  --chapters .cache/weread/candidates.json
```

---

## WeRead原子能力

这些能力是底座，不等于`carl-weread`的全部价值。它们负责把微信读书数据稳定取出来，工作流负责把数据变成判断和行动。

| 能力 | 命令 |
|---|---|
| 查询书架 | `scripts/weread.sh shelf` |
| 书籍搜索 | `scripts/weread.sh search --keyword=画家之眼` |
| 阅读统计 | `scripts/weread.sh readdata` |
| 书籍详情 | `scripts/weread.sh book-info --bookId=BOOK_ID` |
| 章节目录 | `scripts/weread.sh chapters --bookId=BOOK_ID` |
| 阅读进度 | `scripts/weread.sh progress --bookId=BOOK_ID` |
| 笔记概览 | `scripts/weread.sh notebooks --count=20` |
| 个人划线 | `scripts/weread.sh bookmarks --bookId=BOOK_ID` |
| 个人想法 | `scripts/weread.sh mine-reviews --bookid=BOOK_ID` |
| 公开点评 | `scripts/weread.sh reviews --bookId=BOOK_ID` |
| 单条想法 | `scripts/weread.sh review --reviewId=REVIEW_ID` |
| 热门划线 | `scripts/weread.sh best-bookmarks --bookId=BOOK_ID` |
| 章节划线热度 | `scripts/weread.sh underlines --bookId=BOOK_ID --chapterUid=CHAPTER_UID` |
| 章节划线评论 | `scripts/weread.sh readreviews --bookId=BOOK_ID --chapterUid=CHAPTER_UID --reviews='[]'` |
| 推荐好书 | `scripts/weread.sh recommend` |
| 相似书推荐 | `scripts/weread.sh similar --bookId=BOOK_ID` |
| 接口列表 | `scripts/weread.sh list-apis` |

已知兼容处理：

- `readdata`默认补`--mode=overall`，避免服务端返回参数格式错误。
- `recommend`和`similar`默认补`--count=12 --maxIdx=0`，避免部分环境缺分页参数失败。
- `best-bookmarks`默认补`--chapterUid=0`，表示全书热门划线。
- `readreviews --reviews=...`支持JSON数组/对象参数。
- 频率超限时不要反复重试，优先复用`.cache/weread/`或`/private/tmp/`中已保存的候选章节JSON。

---

## 读后行动卡与写回

读完一节后，可以把划线/想法变成行动卡：

```bash
scripts/digest_apply.py \
  --book-title "AI Engineering" \
  --chapter-title "Evals and workflows" \
  --highlight "Agent 不是聊天框，而是模型、工具、上下文和验证的组合。" \
  --current-problem "我在写一篇介绍 carl-weread 的文章，需要把阅读变成可演示动作。"
```

如果已经配置了Obsidian或Folder Mode，可以写回默认目录：

```bash
scripts/digest_apply.py \
  --book-title "AI Engineering" \
  --chapter-title "Evals and workflows" \
  --highlight "Agent 不是聊天框，而是模型、工具、上下文和验证的组合。" \
  --current-problem "我在写文章，需要一个真实案例。" \
  --writeback
```

写回路径形如：

```text
<你的笔记目录>/carl-weread/reading-cards/YYYY-MM-DD-书名-章节.md
```

---

## 本周阅读行动复盘

从一组行动卡生成周复盘：

```bash
scripts/weekly_loop.py \
  --cards /path/to/reading-cards \
  --context "本周在写 Agent Skill 文章，也在验证 carl-weread 的安装链路"
```

它不是微信读书周报的替代品。微信读书周报告诉你「读了多久」，这里要回答：

```text
哪些阅读真的进入了工作？
哪些只是逃避式收藏？
下周只保留哪一条阅读主线？
```

---

## 打开微信读书

推荐输出中会给`weread://`深度链接。它依赖本机微信读书客户端和系统协议注册。更稳妥的输出方式：

```bash
open 'weread://reading?bId=BOOK_ID&chapterUid=CHAPTER_UID'
```

如果没有反应：

1. 安装并打开微信读书客户端。
2. 登录同一个微信读书账号。
3. 再执行上面的`open`命令。
4. 仍然打不开时，用书名和章节名在微信读书里手动搜索。

---

## 目录

```text
carl-weread/
├── SKILL.md
├── README.md
├── carl_weread/
├── scripts/
├── workflows/
├── shared/
└── tests/
```

---

## 当前边界

- V0.2.1已经跑通真实WeRead API、今日推荐、读后行动卡、文件写回、周复盘和测试。
- 目前推荐章节仍以轻量打分为主，还没有完成huashu式「未读书交叉验证推荐」。
- 目前读后行动卡支持用户手动输入划线，还没有完成「自动检查该章是否有划线→无划线追问」协议。
- 目前CLI仍以`scripts/`为主，还没有统一成`carl-weread recommend/after-read/weekly`这种产品级命令。
- 写回会写入真实Obsidian vault或普通文件夹；Chat/WeRead-only模式默认只在对话中返回，不写文件。

---

## 致谢

- 微信读书官方Skill提供了底层API能力：<https://weread.qq.com/r/weread-skills>
- huashu-weread提供了「书架+笔记交叉分析」这个关键启发：<https://github.com/alchaincyf/huashu-weread>
- jerlin-weread启发了CLI化、字段契约和Agent可稳定调用的工程底座。

---

<div align="center">

Made by [LearnPrompt](https://github.com/LearnPrompt) · 为了少读一点，但读准一点

</div>
