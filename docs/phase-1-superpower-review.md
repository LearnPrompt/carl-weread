# carl-weread 一阶段 Superpower 验收

日期：2026-05-19

## 结论

**有条件通过。**

`carl-weread` 的一阶段可以进入验收，但验收口径必须收窄为：

```text
Phase 1: Today Chapter MVP
```

即：

```text
用户一句真实 brief / 最近上下文
→ 微信读书候选章节
→ 今天只读这一小节
→ 读前问题
→ 读后一个动作
```

不要把完整行动卡写回、周复盘、安装分发、复杂排序算法继续塞进一阶段。

## 验收判断

| 项目 | 判断 | 说明 |
|---|---|---|
| 定位清晰度 | 通过 | 「把微信读书变成每日问题解药」足够清楚，明显区别于阅读统计、书单和年报。 |
| Skill 差异化 | 通过 | 重点不是读了多少，而是今天真实问题对应哪一小节。 |
| 主链路完整度 | 通过 | `setup.py`、上下文模式、WeRead候选、`today_live.py` 已形成一键推荐链路。 |
| Agent 接手性 | 基本通过 | README / SKILL / today workflow 足以让另一个 Agent 执行 today-chapter。 |
| 阶段边界 | 有条件通过 | README/SKILL 中仍出现 digest/weekly/行动卡完整闭环叙事，需要明确这些不是一阶段阻塞。 |
| 行动卡写回 | 不进入一阶段 | workflow 已定义，但写回不是当前验收范围。 |
| weekly loop | 不进入一阶段 | 可保留为二阶段 workflow 草案。 |

## 阻塞项

唯一真正阻塞验收的不是代码，而是**范围口径不统一**。

当前材料里同时存在三种口径：

1. README 的 V0.1 闭环：包含读后生成行动卡。
2. phase acceptance 文档：建议冻结在 today 推荐。
3. SKILL 触发范围：包含 today、digest、weekly 三条线。

验收前应明确：

```text
一阶段主链路：today-chapter。
digest-apply：只作为二阶段入口/输出契约，不验收写回。
weekly-loop：二阶段候选，不进入一阶段完成标准。
```

## 非阻塞建议

1. README 后续可以分成三类：
   - 已实现：setup/context/candidates/today_live
   - 契约已定义：digest-apply/weekly-loop
   - 二阶段候选：写回、周复盘、安装分发、排序算法
2. SKILL 中可加阶段说明：
   - Phase 1 stable: today-chapter
   - Experimental contracts: digest-apply, weekly-loop
3. 不要现在升级复杂排序或 embedding；Today MVP 用轻量规则足够验收。

## Superpower 最终意见

可以验收，但必须冻结为：

```text
Today Chapter MVP：根据最近上下文推荐今天只读的一小节，并给出读前问题和读后动作。
```

如果继续把行动卡写回、周复盘、安装体验都纳入一阶段，会导致范围膨胀，无法判断 MVP 是否成立。
