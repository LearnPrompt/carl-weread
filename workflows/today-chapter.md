# Workflow: today-chapter

## 触发

用户说：

- 今天读什么
- 推荐一章
- 根据我最近在做的事找一小节
- 不要推一本书，只推今天能读完的一段

## 目标

从用户最近真实上下文出发，推荐一个微信读书里今天可以完成的小阅读块。

## 标准流程

1. 收集最近上下文
   - 优先：Obsidian 最近 3 天日记、活跃项目文件、最近选题库文件
   - 其次：用户指定的任意 Markdown/TXT 文件夹
   - 再次：用户本轮输入的目标/困惑/项目 brief
   - 最后：没有外部上下文时，仅使用微信读书最近阅读和笔记
2. 收集微信读书数据并生成候选章节
   - 日常使用优先用 `scripts/today_live.py --brief ...` 一键完成真实 WeRead 拉取和推荐
   - 调试候选池时用 `scripts/fetch_candidates.py --output ...` 自动调用 WeRead API
   - 离线/调试时用 `scripts/build_candidates.py` 从已保存 JSON 生成
   - `/shelf/sync` 看最近活跃和已有书
   - `/user/notebooks` 看真读过什么
   - 对候选书调 `/book/chapterinfo`
   - 必要时调 `/book/getprogress`
3. 匹配问题和章节
   - 先提炼用户当前问题，不要直接找热门书
   - 优先选择 5-20 分钟能读完的章节/小节
   - 已经读过但适合重读的章节可以推荐，但必须说明「这是重读」
4. 输出读前问题和读后动作

## 输出模板

```markdown
今天只读这一小节：
《书名》｜章节名

为什么是它：
你最近在处理「X」，表面上是 Y，真正卡住的是 Z。这一节刚好补的是 Z。

读前问题：
带着这个问题读：……

读完只做一个动作：
……

打开：weread://reading?bId=xxx&chapterUid=xxx
```

## 降级策略

- 没有 Obsidian 上下文：先读用户指定的普通 Markdown/TXT 文件夹；还没有就使用本轮对话 brief；再没有才只用微信读书最近阅读，并明确说明口径。
- 没有章节目录：退化为推荐一本书中的最近阅读位置。
- 没有 API Key：提示用户运行 `scripts/setup_api_key.py` 或临时设置 `WEREAD_API_KEY`，不编造结果。
- 候选章节都不明显相关：宁可说明「今天不建议读新书」，改推荐整理已有笔记。
