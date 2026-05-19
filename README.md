<div align="center">

# carl-weread

> 把微信读书从「读了多少」改成「今天哪个问题可以被读懂一点」。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-blueviolet)](SKILL.md)
[![WeRead API](https://img.shields.io/badge/WeRead-API-green)](https://weread.qq.com/r/weread-skills)

<br>

**微信读书行动型阅读教练：根据当前问题，推荐一本书里的今天一小节，并把阅读变成行动卡。**

<br>

官方微信读书已经有书架、搜索、笔记、统计和推荐。它能回答「你读了多久」「有哪些书」「这本书有哪些笔记」。

`carl-weread`想多走一步：你现在卡住的事，微信读书里哪本书、哪一节，能帮你今天少囤一点资料，多做一个判断？

```text
当前问题 → 书架/笔记/章节交叉 → 推荐一本书的一小节 → 读后行动卡 → Markdown回流 → 周阅读行动复盘
```

[看差异](#看差异) · [功能总览](#功能总览) · [核心方法](#核心方法) · [触发话术](#触发话术) · [装上就能用](#装上就能用)

</div>

---

## 看差异

同样一个问题：

> 我最近信息焦虑，总是在囤资料但不产出，今天该读什么？

普通推荐很容易给一串书名：信息管理、效率、认知、写作、项目管理。书可能都对，但问题还在原地。

真正需要被回答的是：

- 我现在是缺信息，还是缺一个能收束问题的框架？
- 这本书我是不是早就收藏过、读过、划过线？
- 今天到底读哪一小节，读完以后做什么？

`carl-weread`要给的是一个能在今天完成的小切口：

```markdown
今天只读这一小节：
《某本书》｜某一章

为什么是它：
资料已经够多，真正卡住的是问题没有收束。这一节刚好能把「继续搜索」改成「提出一个更好的问题」。

读前问题：
我现在反复搜索，是为了做哪个判断？

读完只做一个动作：
把当前文章选题改写成一个问题句，别再扩成资料清单。

打开：weread://reading?bId=...&chapterUid=...
```

一句话定位：

```text
carl-weread更像「今天这个问题，只读哪一节，然后怎么用」。
```

---

## 和原版/参考项目的区别

| 项目 | 更像什么 | 强项 | carl-weread的差异 |
|---|---|---|---|
| 微信读书官方能力（App统计 / WeRead Skill） | 阅读数据与原子接口 | 书架、搜索、笔记、统计、推荐接口完整 | 不停在查数据，往「当前问题→章节→行动」走 |
| huashu-weread | 读书顾问 | 书架+笔记交叉，推荐下一本书，规划主题路径 | 参考它的交叉分析思路，但把目标缩到「今天只读哪一节」 |
| jerlin-weread | CLI工程底座 | API文档、脚本、字段约束更稳 | 学它的命令化组织方式，再把命令接成阅读工作流 |
| yao-weread-skill | 阅读报告 | 年度/周期阅读可视化，适合展示 | 不追求报告漂亮，优先看阅读有没有进入工作 |

---

## 功能总览

| 能力 | 当前状态 | 做什么 | 入口 |
|---|---:|---|---|
| API Key安全初始化 | ✅ 已完成 | 将key写入私有文件，权限600，不进仓库 | `scripts/setup_api_key.py` |
| 上下文模式 | ✅ 已完成 | 支持Obsidian、普通文件夹、Chat、WeRead-only四档上下文 | `scripts/setup.py --mode ...` |
| 今日推荐 | ✅ 已完成 | 拉取真实WeRead数据，根据当前问题推荐一本书里的一节 | 自然语言触发 / `scripts/today_live.py` |
| 读后行动卡 | ✅ 已完成 | 把书名、章节、划线、当前问题压成一张行动卡 | 自然语言触发 / `scripts/digest_apply.py` |
| 写回Obsidian/本地文件夹 | ✅ 已完成 | 把阅读行动卡写回`carl-weread/reading-cards/` | `--writeback` |
| 周阅读行动复盘 | ✅ 已完成 | 从行动卡看哪些阅读真的进入了文章、项目和判断 | 自然语言触发 / `scripts/weekly_loop.py` |
| WeRead原子API helper | ✅ 已完成 | 书架、搜索、统计、详情、目录、进度、笔记、划线、点评、推荐 | `scripts/weread.sh ...` |
| 未读书交叉验证推荐 | 🚧 下一版重点 | 过滤已深读/只收藏/已消化，推荐真正没读过但现在该读的书 | V0.3计划 |
| 苏格拉底式无划线协议 | 🚧 下一版重点 | 读完后先查有没有划线；没有划线就用问题追回理解 | V0.3计划 |
| 统一产品级CLI | 🚧 下一版重点 | 从一堆`scripts/`升级成`carl-weread recommend/after-read/weekly` | V0.3计划 |

---

## 核心方法

### 1. 先问问题，再找书

很多阅读推荐从主题开始，比如AI、产品、心理学。`carl-weread`先看你现在卡在哪里。

| 用户输入 | 先判断什么 | 阅读目标 |
|---|---|---|
| 我信息焦虑 | 是缺信息，还是缺收束问题的方法 | 减少输入，形成判断 |
| 我写文章卡住了 | 是缺案例，缺结构，还是缺一个反常识角度 | 推进一篇具体内容 |
| 我项目推进慢 | 是缺技术方案，缺产品判断，还是缺下一步动作 | 读完能改一个动作 |
| 我不知道读什么 | 是真没方向，还是收藏太多没有消化 | 少推荐，多收束 |

### 2. 书架、笔记、章节要交叉看

单看书架，会把「收藏过」误判成「真的需要」。单看笔记，又容易只围着旧兴趣转。`carl-weread`把几类数据放在一起看：

| 数据源 | 接口 | 揭示什么 | 用在什么地方 |
|---|---|---|---|
| 书架 | `/shelf/sync` | 用户主动收藏/分类的兴趣 | 找候选书，不当作唯一证据 |
| 笔记本概览 | `/user/notebooks` | 真读过什么、哪些书有痕迹 | 判断深读、浅读、只收藏 |
| 章节目录 | `/book/chapterinfo` | 今天能不能定位到小节 | 避免只推荐一本书 |
| 阅读进度 | `/book/getprogress` | 是否正在读、读到哪里 | 避免推荐明显不合适的位置 |
| 个人划线 | `/book/bookmarklist` | 用户真正停下来的地方 | 读后行动卡的证据 |
| 热门划线/点评 | `/book/bestbookmarks`、`/review/list` | 大家反复标记的问题 | 辅助判断章节价值 |
| 推荐/相似书 | `/book/recommend`、`/book/similar` | 新候选来源 | V0.3做未读书推荐交叉验证 |

### 3. 阅读统计不比时长，比影响

微信读书已经能告诉你读了多久。这里不再做一个低配统计页。

`weekly-loop`关心的是：

```text
这周哪次阅读变成了文章角度？
哪条划线进入了项目决策？
哪本书只是制造了收藏安全感？
下周只保留哪一条阅读主线？
```

所以它吃的输入包括：

```text
微信读书统计 + 本周划线/行动卡 + Obsidian项目/选题上下文
```

---

## 触发话术

| 你可以这样说 | 走哪个能力 | 预期输出 |
|---|---|---|
| 今天读哪一小节 | today-chapter | 一本书里的一个章节/小节，附读前问题和行动 |
| 根据我的书架和最近问题，推荐一本现在最该读的书，只告诉我今天读哪一节 | today-chapter | 书名、章节、推荐理由、打开链接 |
| 我信息焦虑，帮我少读一点但读准一点 | today-chapter / V0.3 socratic-read | 先收束问题，再推荐小阅读块 |
| 这本书我读到哪了 | 原子能力：progress | 阅读进度和打开链接 |
| 查一下这本书的目录和我的划线 | 原子能力：book-info/bookmarks/chapters | 书籍详情、章节目录、个人划线 |
| 读完了，帮我消化成行动 | digest-apply | 阅读行动卡、一个最小行动、选题线索 |
| 把这次阅读闭环存到Obsidian | writeback | 写入`carl-weread/reading-cards/` |
| 本周阅读行动复盘 | weekly-loop | 本周真正进入工作的阅读、逃避式收藏、下周主线 |
| 给我推荐一本我没读过但现在该读的书 | V0.3 unread-advisor | 交叉验证已读/未读后推荐一本新书 |

---

## 装上就能用

先说结论：如果你只是想让Agent理解这套阅读方法，安装`SKILL.md`就够；如果你要运行微信读书API、脚本、测试和写回功能，需要clone完整仓库。

### 轻量安装：只让Agent读到说明

```bash
hermes skills install https://raw.githubusercontent.com/LearnPrompt/carl-weread/main/SKILL.md
```

这一步只会安装`SKILL.md`。它适合加载使用说明，但不会带上`scripts/`、`carl_weread/`、`workflows/`和测试文件。

为什么不像有些Skill一样一行安装就能跑？原因很简单：`carl-weread`现在带了Python模块、Shell脚本、测试和本地写回逻辑。Hermes安装raw `SKILL.md`时，只会读取那个文件，不会自动把整个GitHub仓库复制下来。

### 完整安装：真正运行这套工具

```bash
git clone https://github.com/LearnPrompt/carl-weread ~/.hermes/skills/carl-weread
cd ~/.hermes/skills/carl-weread
python3 -m venv .venv
.venv/bin/python -m pip install -U pip pytest
.venv/bin/python -m pytest tests -q
```

如果你已经clone了仓库，也可以在仓库里跑安装脚本：

```bash
scripts/install_skill.py
```

### 配置微信读书API Key

自然语言版：

```text
帮我配置carl-weread的微信读书API Key。不要把key写进仓库，也不要在回复里打印key。
```

代码版：

```bash
scripts/setup_api_key.py
```

它会把key写入`~/.config/carl-weread/api_key`，文件权限为`600`，不会写入`config.toml`，也不会打印key。

也可以只在当前shell临时使用：

```bash
export WEREAD_API_KEY="<你的微信读书API Key>"
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

首次配置也给两种说法。

自然语言版：

```text
帮我把carl-weread配置成WeRead-only模式。先不接Obsidian，只根据我的微信读书书架、笔记和阅读进度推荐。
```

代码版：

```bash
# Obsidian用户
scripts/setup.py --mode obsidian --path "/path/to/your/vault"

# 非Obsidian，但有本地Markdown/TXT笔记
scripts/setup.py --mode folder --path "/path/to/your/notes"

# 只使用当前对话上下文
scripts/setup.py --mode chat

# 只使用微信读书数据
scripts/setup.py --mode weread-only
```

配置默认写入：`~/.config/carl-weread/config.toml`。

---

## 今日推荐：一本书里的一小节

自然语言版：

```text
根据我的微信读书书架和最近问题，推荐一本现在最该读的书，并告诉我今天只读哪一节。
我的问题是：我正在写一篇微信读书Skill文章，想找一个能推进文章结构的阅读切口。
```

代码版：

```bash
scripts/today_live.py \
  --brief "我正在写一篇微信读书Skill文章，请根据我的书架推荐一本最适合现在读的书，并告诉我今天只读哪一节。"
```

它会自动做这些事：

```text
读取配置 → 收集上下文 → 拉微信读书书架/笔记/章节 → 选择一本书里的一小节 → 输出读前问题和读后动作
```

重点放在少一点：只给今天能读完、能接上当前问题的一节。

---

## 读后行动卡与写回

行动卡要贴着书走。它必须带着书名、章节、划线/想法和当前问题一起生成，否则就会变成空泛总结。

自然语言版：

```text
我刚读完《AI Engineering》的「Evals and workflows」。
这句划线对我有用：Agent的价值在模型、工具、上下文和验证之间。
我现在的问题是：我在写一篇介绍carl-weread的文章，需要把阅读变成可演示动作。
请把这次阅读消化成一张行动卡；如果已经配置写回，就存到我的笔记目录。
```

代码版：

```bash
scripts/digest_apply.py \
  --book-title "AI Engineering" \
  --chapter-title "Evals and workflows" \
  --highlight "Agent的价值在模型、工具、上下文和验证之间。" \
  --current-problem "我在写一篇介绍carl-weread的文章，需要把阅读变成可演示动作。" \
  --writeback
```

写回路径形如：

```text
<你的笔记目录>/carl-weread/reading-cards/YYYY-MM-DD-书名-章节.md
```

这张卡会保留「哪本书、哪一节、哪条划线、解决什么问题、下一步做什么」。周复盘从这些卡里读证据，避免空泛总结。

---

## 本周阅读行动复盘

自然语言版：

```text
基于本周carl-weread写回的阅读行动卡，帮我做一次阅读复盘。
重点看：哪些阅读进入了文章或项目，哪些只是收藏安全感，下周只保留哪一条阅读主线。
```

代码版：

```bash
scripts/weekly_loop.py \
  --cards /path/to/reading-cards \
  --context "本周在写Agent Skill文章，也在验证carl-weread的安装链路"
```

这里不重复微信读书周报。微信读书周报告诉你「读了多久」，这里要回答：

```text
哪本书的哪一节真的推进了工作？
哪条划线变成了文章角度或项目动作？
哪些收藏只是缓解焦虑？
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

## 仓库结构

这段给人和Agent快速定位文件，不写也不会影响`SKILL.md`被读取；但完整clone仓库时，它能让Agent更快找到脚本、工作流和测试位置。

```text
carl-weread/
├── SKILL.md          # Agent读取的技能说明
├── README.md         # 给人看的产品说明和安装指南
├── carl_weread/      # Python核心逻辑
├── scripts/          # 可直接运行的命令入口
├── workflows/        # 可复用工作流说明
├── shared/           # 输出风格等共享约定
└── tests/            # 回归测试
```

---

## 当前边界

- V0.2.1已经跑通真实WeRead API、今日推荐、读后行动卡、文件写回、周复盘和测试。
- 目前推荐章节仍以轻量打分为主，还没有完成「未读书交叉验证推荐」。
- 目前读后行动卡支持用户手动输入划线，还没有完成「自动检查该章是否有划线→无划线追问」协议。
- 目前CLI仍以`scripts/`为主，还没有统一成`carl-weread recommend/after-read/weekly`这种产品级命令。
- 写回会写入真实Obsidian vault或普通文件夹；Chat/WeRead-only模式默认只在对话中返回，不写文件。

---

## 开发者附录：WeRead原子能力

普通用户可以跳过这里。这一节给开发者调试接口、排查字段和复用底层API。

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

开发者如果只想调试候选章节生成，可以拆开跑：

```bash
scripts/fetch_candidates.py \
  --output .cache/weread/candidates.json \
  --limit-books 5

scripts/today.py \
  --config ~/.config/carl-weread/config.toml \
  --brief "我最近在做一个可分享的微信读书Skill" \
  --chapters .cache/weread/candidates.json
```

---

## 致谢

- 微信读书官方API提供底层能力：<https://weread.qq.com/r/weread-skills>
- huashu-weread提供了「书架+笔记交叉分析」这个关键启发：<https://github.com/alchaincyf/huashu-weread>
- jerlin-weread启发了CLI化、字段契约和Agent可稳定调用的工程底座：<https://github.com/jerlinn/jerlin-weread>
- yao-weread-skill启发了阅读报告和展示型输出。

---

<div align="center">

Made by [LearnPrompt](https://github.com/LearnPrompt) · 为了少读一点，但读准一点

</div>
