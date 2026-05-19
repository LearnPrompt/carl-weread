# carl-weread

把微信读书变成你的每日问题解药。

很多读书工具都在问：你读了多少书？

`carl-weread` 问的是另一个问题：你今天遇到的真实问题，哪本书里的哪一小节能帮你往前走一步？

它会读取你的微信读书书架、笔记和最近阅读，再结合你的 Obsidian 日记、项目和选题，推荐一个今天能读完的小阅读块。读完后，它把收获变成行动卡，回流到你的项目和内容创作里。

## 现在的 V0.2：文章可演示完成版

V0.2 已经把主链路补成可演示闭环：

```text
最近真实上下文 → 识别当下问题 → 匹配微信读书的一章/一小节 → 给读前问题 → 读后生成行动卡
```

已完成：

- `scripts/weread.sh`：微信读书 API 的薄 CLI 包装层。
- `carl_weread/config.py`：首次配置与上下文模式（Obsidian/Folder/Chat/WeRead-only）。
- `carl_weread/context.py`：从 Obsidian 或普通笔记文件夹收集最近上下文。
- `carl_weread/today_chapter.py`：从候选章节中选择今天的一小节。
- `scripts/today.py`：把配置、上下文和候选章节文件串成可运行的今日推荐。
- `carl_weread/candidates.py`：把 WeRead 书架、笔记、章节目录响应标准化成候选章节。
- `scripts/build_candidates.py`：从已保存的 WeRead API JSON 构建候选章节文件。
- `scripts/fetch_candidates.py`：调用 `scripts/weread.sh` 拉取真实 WeRead 数据并生成候选章节文件。
- `scripts/today_live.py`：一键拉取真实 WeRead 数据并输出今日一小节推荐，不需要中间候选文件。
- `carl_weread/digest_apply.py` + `scripts/digest_apply.py`：把读后划线生成阅读行动卡，可输出或写回。
- `carl_weread/writeback.py`：按 Obsidian/Folder/Chat/WeRead-only 模式处理落盘。
- `carl_weread/weekly_loop.py` + `scripts/weekly_loop.py`：从本周行动卡生成阅读行动复盘。
- `scripts/install_skill.py`：把完整仓库安装成 Hermes skill 目录，避免只安装 `SKILL.md`。
- `SKILL.md` + `workflows/`：Agent Skill 工作流契约。
- `tests/`：覆盖 API helper、配置、上下文、推荐、行动卡、写回、周复盘。


## 完整安装到新的 Hermes Agent

如果只是执行：

```bash
hermes skills install https://raw.githubusercontent.com/LearnPrompt/carl-weread/main/SKILL.md
```

Hermes 只会安装 `SKILL.md`，适合加载说明，但不会带上 `scripts/`、`carl_weread/` 和测试文件。

要完整体验这个 skill，推荐在新 Agent 机器上直接 clone 整个仓库：

```bash
git clone https://github.com/LearnPrompt/carl-weread ~/.hermes/skills/carl-weread
cd ~/.hermes/skills/carl-weread
python3 -m venv .venv
.venv/bin/python -m pip install -U pip pytest
.venv/bin/python -m pytest tests -q
```

或者在已 clone 的仓库里执行完整安装脚本：

```bash
scripts/install_skill.py
```

然后在新 Agent 的环境里配置：

```bash
export WEREAD_API_KEY="wrk-你的微信读书 API Key"
```

## 安装前置

`carl-weread` 不要求用户先安装官方 WeRead Skill；它把微信读书 API 调用封装在自己的 `scripts/weread.sh` 里。

但它需要官方微信读书 API Key：

```bash
export WEREAD_API_KEY="wrk-你的微信读书 API Key"
```

API Key 获取入口：<https://weread.qq.com/r/weread-skills>

如果本机已经安装官方 WeRead Skill，可以把它当作 API 契约参考；`carl-weread` 的目标不是替代官方原子能力，而是在其上层增加「上下文 → 章节 → 行动」工作流。

## 没有 Obsidian 怎么用

可以用，而且应该被设计成可用。Obsidian 只是最高配上下文源，不是硬依赖。

推荐做四档模式：

| 模式 | 适合谁 | 上下文来源 | 输出能力 |
|---|---|---|---|
| Full Mode | Obsidian 用户 | 日记、项目、选题库 + 微信读书 | 最完整的行动闭环 |
| Folder Mode | 有本地笔记但不用 Obsidian | 任意 Markdown/TXT 文件夹 + 微信读书 | 可推荐章节并生成行动卡 |
| Chat Mode | 只在 Agent 里聊天 | 用户当前一句话/最近对话 + 微信读书 | 轻量推荐今天一小节 |
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

`WEREAD_API_KEY` 只从环境变量读取，不会写入配置文件。

代码层面已经支持 Folder Mode 和 Chat Mode：

```bash
scripts/collect_context.py --config ~/.config/carl-weread/config.toml --brief "我最近在做一个可分享的微信读书 skill"
```

## 快速验证

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -U pip pytest
.venv/bin/python -m pytest tests -q
```

## 一键今日推荐

完成配置和 `WEREAD_API_KEY` 后，日常使用可以直接跑：

```bash
scripts/today_live.py \
  --brief "我今天卡在内容选题和项目推进之间"
```

它会自动完成：

```text
读取配置 → 收集上下文 → 拉微信读书书架/笔记/章节 → 选择今天一小节 → 输出读前问题和读后动作
```

如果只想调试候选章节生成，可以继续使用下面的拆分命令。

## 候选章节生成

有 `WEREAD_API_KEY` 后，可以直接从真实微信读书数据生成候选章节：

```bash
scripts/fetch_candidates.py \
  --output .cache/weread/candidates.json \
  --limit-books 5
```

它会调用：

```text
scripts/weread.sh shelf
scripts/weread.sh notebooks --count=200
scripts/weread.sh chapters --bookId=...
```

然后生成 `scripts/today.py` 可直接使用的 JSON。

如果已经手动保存了 API 响应，也可以离线构建：

```bash
scripts/build_candidates.py \
  --shelf .cache/weread/shelf.json \
  --notebooks .cache/weread/notebooks.json \
  --chapter-dir .cache/weread/chapters \
  --output .cache/weread/candidates.json
```

## 本地 today 验证

拿到候选章节 JSON 后，可以验证完整推荐闭环：

```bash
scripts/today.py \
  --config ~/.config/carl-weread/config.toml \
  --brief "我最近在做一个可分享的微信读书 skill" \
  --chapters examples/chapters.json
```

输出会遵守「今天只读这一小节 → 为什么是它 → 读前问题 → 读后动作 → weread:// 链接」格式。

## API helper

```bash
scripts/weread.sh shelf
scripts/weread.sh notebooks --count=200
scripts/weread.sh search --keyword=AI
scripts/weread.sh chapters --bookId=BOOK_ID
scripts/weread.sh progress --bookId=BOOK_ID
```


## 读后行动卡与写回

读完一节后，可以把划线/想法变成行动卡：

```bash
scripts/digest_apply.py \
  --book-title "AI Engineering" \
  --chapter-title "Evals and workflows" \
  --highlight "Agent 不是聊天框，而是模型、工具、上下文和验证的组合。" \
  --current-problem "我在写一篇介绍 carl-weread 的文章，需要把阅读变成可演示动作。"
```

如果已经配置了 Obsidian 或 Folder Mode，可以写回到默认目录：

```bash
scripts/digest_apply.py \
  --book-title "AI Engineering" \
  --chapter-title "Evals and workflows" \
  --highlight "Agent 不是聊天框，而是模型、工具、上下文和验证的组合。" \
  --current-problem "我在写文章，需要一个真实案例。" \
  --writeback
```

## 本周阅读行动复盘

从一组行动卡生成周复盘：

```bash
scripts/weekly_loop.py \
  --cards /path/to/reading-cards \
  --context "本周在写 Agent Skill 文章，也在验证 carl-weread 的安装链路"
```

## Skill 入口

典型触发语：

- 「今天读哪一小节」
- 「根据我最近在做的事推荐一章」
- 「读完了，帮我消化成行动」
- 「把这次阅读闭环存到 Obsidian」
- 「本周阅读行动复盘」

## 和其他项目的区别

| 项目 | 更像什么 | carl-weread 怎么不同 |
|---|---|---|
| 官方 WeRead Skill | 原子 API | carl-weread 关注上下文驱动行动 |
| jerlin-weread | 稳定 CLI 底座 | carl-weread 学它的工程化，但往行动工作流走 |
| huashu-weread | 读书顾问 | carl-weread 不只推荐下一本，而是推荐今天这一节 |
| yao-weread-skill | 阅读报告 | carl-weread 不做展示型复盘，做行动型闭环 |
| qiaomu-epub-book-generator | 外部材料转 EPUB | carl-weread 后续可接它做输入侧扩展 |

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

## 当前边界

- 今日推荐、读后行动卡、文件写回、周复盘都已经有可运行 CLI 和测试。
- 真实 API 字段兼容性已按当前样本适配，但后续仍建议用更多书籍类型继续加固。
- 写回会写入真实 Obsidian vault 或普通文件夹；Chat/WeRead-only 模式默认只在对话中返回，不写文件。
