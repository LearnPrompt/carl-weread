# carl-weread

把微信读书变成你的每日问题解药。

很多读书工具都在问：你读了多少书？

`carl-weread` 问的是另一个问题：你今天遇到的真实问题，哪本书里的哪一小节能帮你往前走一步？

它会读取你的微信读书书架、笔记和最近阅读，再结合你的 Obsidian 日记、项目和选题，推荐一个今天能读完的小阅读块。读完后，它把收获变成行动卡，回流到你的项目和内容创作里。

## 现在的 V0.1

V0.1 先不做大而全，只验证一个闭环：

```text
最近真实上下文 → 识别当下问题 → 匹配微信读书的一章/一小节 → 给读前问题 → 读后生成行动卡
```

已搭建：

- `scripts/weread.sh`：微信读书 API 的薄 CLI 包装层。
- `carl_weread/context.py`：从 Obsidian 收集最近上下文。
- `carl_weread/today_chapter.py`：从候选章节中选择今天的一小节。
- `SKILL.md` + `workflows/`：Agent Skill 工作流契约。
- `tests/`：核心格式化、上下文收集、章节选择的测试。

## 安装前置

```bash
export WEREAD_API_KEY="wrk-你的微信读书 API Key"
```

API Key 获取入口：<https://weread.qq.com/r/weread-skills>

## 快速验证

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -U pip pytest
.venv/bin/python -m pytest tests -q
```

## API helper

```bash
scripts/weread.sh shelf
scripts/weread.sh notebooks --count=200
scripts/weread.sh search --keyword=AI
scripts/weread.sh chapters --bookId=BOOK_ID
scripts/weread.sh progress --bookId=BOOK_ID
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

## 下一步

- 接入真实微信读书 API 响应，生成候选章节列表。
- 把 Obsidian 上下文和 WeRead 章节选择串成一个 `today` 命令。
- 生成「阅读行动卡」并写回 Obsidian。
