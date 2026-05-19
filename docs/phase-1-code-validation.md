# carl-weread 一阶段代码与安全验收

日期：2026-05-19

## 结论

**有条件通过。**

当前代码可以进入一阶段验收，不建议继续扩展功能。验收阻塞点不是测试失败或安全问题，而是：

1. 当前环境没有 `WEREAD_API_KEY`，无法跑真实 WeRead API 端到端。
2. `today_live.py` 在默认配置文件不存在时错误提示不够友好，这是体验问题，不阻塞一阶段概念验收。
3. 真实 API 字段兼容性还需要二阶段用脱敏样本加固。

## 已执行检查

### 1. 测试

命令：

```bash
.venv/bin/python -m pytest tests -q
```

结果：

```text
25 passed in 0.39s
```

### 2. 编译检查

命令：

```bash
.venv/bin/python -m compileall carl_weread scripts -q
```

结果：通过，无报错。

### 3. Skill 基础检查

- `scripts/weread.sh --help`：exit code 0
- `SKILL.md` description 长度：131 字符
- description 小于 1024：通过

### 4. 安全边界检查

检查目标：

- 是否硬编码真实 API Key / token / password / secret
- 是否出现 `shell=True`、`os.system`、`eval`、`exec`、`pickle.loads`
- `WEREAD_API_KEY` 是否只从环境变量读取

结果：

- 未发现新增危险执行模式。
- 未发现真实密钥硬编码。
- 仓库中出现的 `wrk-secret` 是测试假值，用于验证不泄露 API Key，不是真实凭据。
- `WEREAD_API_KEY` 的使用符合当前约定：只从环境变量读取，不写入配置文件，不作为正常命令行参数传入。

## 当前已覆盖的关键路径

| 路径 | 状态 |
|---|---|
| 配置读写不保存 API Key | 已有测试 |
| Obsidian / Folder / Chat / WeRead-only 模式 | 已有测试 |
| 普通文件夹 fallback | 已有测试 |
| 候选章节标准化 | 已有测试 |
| 从 fake WeRead helper 拉候选 | 已有测试 |
| `fetch_candidates.py` 不接受 `--api-key` | 已有测试 |
| `today_live.py` 不接受 `--api-key` | 已有测试 |
| 一键 today live fake helper 成功路径 | 已有测试 |
| 无 API Key 安全失败 | 已有测试 |

## 不阻塞一阶段的已知问题

### 1. 当前环境没有真实 `WEREAD_API_KEY`

因此无法验证真实 WeRead API 响应字段。当前 candidates 模块是防御式兼容：

- book id 支持 `bookId` / `book_id` / `id`
- 书名支持 `title` / `bookName` / `name`
- chapter id 支持 `chapterUid` / `uid` / `chapterId`
- 章节名支持 `chapterName` / `title`

但这还需要真实脱敏样本验证。

### 2. 默认配置缺失时提示不友好

已知现象：未提供 `--config` 且默认配置不存在时，`today_live.py` 会抛 `FileNotFoundError`。

建议二阶段或验收后第一修复：

```text
找不到配置文件：~/.config/carl-weread/config.toml
请先运行：scripts/setup.py --mode chat
```

并返回 exit code 2。

这不影响当前一阶段主链路验收，因为提供 config 时无 Key 安全失败路径已经正常。

### 3. 独立代码审查子任务超时

尝试调用独立 code/security reviewer 子任务时发生超时。已用本地测试、编译、静态搜索和手动检查补充完成验收。该超时不代表项目测试失败。

## 验收意见

代码层面可以冻结一阶段。

当前不要继续补功能，建议只做：

1. 保存验收报告。
2. 整理 commit / branch。
3. 用真实脱敏 API 样本作为二阶段第一批测试输入。
