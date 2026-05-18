# Data Contract

## WeRead 时间和单位

- Unix 时间戳：展示为 `YYYY-MM-DD`。
- 阅读时长：接口单位通常是秒，展示为「X 小时 Y 分钟」。
- 进度：展示为百分比，不直接输出原始数字口径。

## Deep Link

| 场景 | 格式 |
|---|---|
| 打开书籍 | `weread://reading?bId={bookId}` |
| 打开章节 | `weread://reading?bId={bookId}&chapterUid={chapterUid}` |

## 输出边界

- 不输出 API Key。
- 不导出书籍全文。
- 用户自己的划线和想法可用于总结，但公开发布前应提醒隐私风险。
