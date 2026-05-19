# carl-weread 一阶段验收报告

日期：2026-05-19

## 结论

一阶段已经不适合继续无边界迭代。当前应进入 Superpower / Office Hours 验收。

按「最小可验收版本」口径，完成度约 85%。
按 README 里写的完整 V0.1 闭环口径，完成度约 75%-80%。

差距主要不在主体链路，而在两个尾部能力：

1. 真实 WeRead API 样本下的字段兼容性还没有用真实 Key 跑通。
2. 「读后行动卡写回」目前有 workflow 与输出契约，但还没有完整代码实现。

因此建议冻结一阶段开发，只做验收、记录问题、再决定二阶段范围。

## 一阶段原始目标

V0.1 要验证的闭环是：

```text
最近真实上下文 → 识别当下问题 → 匹配微信读书的一章/一小节 → 给读前问题 → 读后生成行动卡
```

## 当前完成情况

| 模块 | 状态 | 说明 |
|---|---:|---|
| Skill 定位与差异化 | 已完成 | README 和 SKILL.md 已明确：不是阅读统计，而是上下文驱动的阅读行动系统。 |
| 不依赖官方 WeRead Skill | 已完成 | 项目自带 `scripts/weread.sh`，只要求 `WEREAD_API_KEY`。 |
| API Key 安全边界 | 已完成 | Key 只从环境变量读取，不写入配置，不作为命令行参数传入。 |
| 无 Obsidian 用户支持 | 已完成 | 支持 Obsidian / Folder / Chat / WeRead-only 四档模式。 |
| 首次配置 | 已完成 | `scripts/setup.py --mode ...` 可生成配置。 |
| 上下文收集 | 已完成 | `collect_context_for_config(...)` 支持多模式降级。 |
| 候选章节构建 | 已完成 | `carl_weread/candidates.py`、`build_candidates.py`、`fetch_candidates.py` 已实现。 |
| 今日章节推荐 | 已完成 | `today.py` 可用本地候选章节生成推荐。 |
| 一键命令 | 已完成 | `today_live.py` 可串联配置、上下文、WeRead 数据和今日推荐。 |
| 输出风格 | 已完成 | `shared/output-style.md` 规定必须包含章节、理由、读前问题、读后动作、weread 链接。 |
| 测试 | 已完成 | 当前测试通过：25 passed。 |
| 真实 API 样本加固 | 部分完成 | 已做防御式字段兼容，但当前环境没有 `WEREAD_API_KEY`，未跑真实样本。 |
| 读后行动卡写回 | 未完成 | workflow 已定义，代码尚未实现写回 Obsidian / folder / chat。 |
| 包安装 / CLI entrypoint | 未完成 | 目前仍以 `scripts/*.py` 方式运行。 |

## 验证结果

最近一次测试：

```bash
.venv/bin/python -m pytest tests -q
```

结果：

```text
25 passed in 0.39s
```

工作区当前仍有未提交修改和新增文件，验收前建议不要继续加功能，而是整理 commit 或打验收分支。

## 不建议继续迭代的原因

继续写新功能会把一阶段变成开放式开发，难以判断 MVP 是否成立。

当前已经可以验收的核心问题是：

> 这个 Skill 的差异化是不是成立？
> 用户是否真的需要「今天只读这一小节」？
> 四档上下文降级是否足够降低安装门槛？
> WeRead 数据和用户当前问题之间的匹配是否值得继续投入？

这些问题需要 Superpower / Office Hours 评价，而不是继续写代码解决。

## 给 Superpower 的验收重点

请重点看：

1. Skill 的定位是否足够清晰。
2. V0.1 是否过大，是否应该缩成「today chapter」一个闭环。
3. 四档模式是否让非 Obsidian 用户也能上手。
4. 当前 README / SKILL.md / workflows 是否能让另一个 Agent 接手。
5. 是否应该把「行动卡写回」放到二阶段，而不是一阶段继续补。

## 给 Office Hours 的验收重点

请重点问：

1. 真实需求：用户是真的想读更多，还是想把阅读变成行动？
2. 现状替代：用户现在用什么方式决定今天读什么？痛点强不强？
3. 最窄切口：是否只保留「根据一句 brief 推荐微信读书一小节」作为首发？
4. 观察证据：卡尔自己是否会连续 7 天使用？
5. 未来扩展：如果这个切口成立，是否自然扩展到行动卡、周复盘、内容选题？

## 建议冻结范围

一阶段冻结在：

```text
setup.py
→ today_live.py
→ 输出今天一小节推荐
```

不要继续把以下内容塞进一阶段：

- Obsidian 写回完整实现
- 周复盘自动化
- 包发布和安装器
- 多平台同步
- 更复杂的排序算法

这些应进入二阶段候选池。

## 建议下一步

1. 停止新增功能。
2. 整理当前 diff，形成验收 commit 或验收分支。
3. 把本报告、README、SKILL.md、workflow 文件交给 Superpower / Office Hours。
4. 根据验收结论决定二阶段只做一个方向：
   - A：真实 API 字段兼容 + 排序策略
   - B：读后行动卡写回
   - C：安装和分发体验

我的建议：二阶段优先做 B，但必须等验收后再定。
